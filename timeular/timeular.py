import requests
import json
import datetime
import tzlocal
import re

_V3 = 'https://api.timeular.com/api/v3'
_ISO_8601 = re.compile(r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$')


def _parse_datetime(dt):
  return datetime.datetime.fromisoformat(dt)

def _dump_datetime(dt):
  if dt.microsecond == 0:
    dt = dt + datetime.timedelta(microseconds=1)
  return dt.isoformat()[:-3]

def _parse_all_dts(d):
  """ given dictionary with strings that should be dates, replace them with dates """
  if type(d) is dict:
    for k in d:
      if type(d[k]) is dict:
        _parse_all_dts(d[k])
      if type(d[k]) is str and re.match(_ISO_8601, d[k]):
        d[k] = _parse_datetime(d[k])
  if type(d) is list:
    for e in d:
      if type(e) is dict:
        _parse_all_dts(e)
  return d


class TimeularSession(object):

  def __init__(self, api_key, api_secret, no_edit_mode=True, verbose=False):
    self._VERBOSE = verbose
    self._edit_lock = no_edit_mode
    self._sess = requests.Session()
    self._sess.headers.update({
      'Content-Type': 'application/json'
    })
    self._active_device = None
    self._sign_in(api_key, api_secret)


  def __enter__(self):
    return self


  def __exit__(self, exc_type, exc_value, exc_traceback):
    self._sess.close()


  def _get(self, path, params={}, return_text=False):
    resp = self._sess.request(
      "GET", f"{_V3}/{path}", params=params
    )
    if self._VERBOSE:
      print(f"GET  v3/{path} -- {resp.status_code}")
      if resp.status_code != 200:
        print(resp.text)
    if return_text:
      return resp.text
    return _parse_all_dts(resp.json())


  def _post(self, path, payload):
    resp = self._sess.request(
      "POST", f"{_V3}/{path}", data=json.dumps(payload)
    )
    if self._VERBOSE:
      print(f"POST v3/{path} -- {resp.status_code}")
      if resp.status_code != 200:
        print(resp.text)
    return resp.json()


  def _patch(self, path, payload):
    assert not self._edit_lock, "this session was initiated with no_edit_mode=True"
    print(payload)
    resp = self._sess.request(
      "PATCH", f"{_V3}/{path}", data=json.dumps(payload)
    )
    if self._VERBOSE:
      print(f"PATCH v3/{path} -- {resp.status_code}")
      if resp.status_code != 200:
        print(resp.text)
    return _parse_all_dts(resp.json())


  def _del(self, path):
    assert not self._edit_lock, "this session was initiated with no_edit_mode=True"
    resp = self._sess.request(
      "DELETE", f"{_V3}/{path}"
    )
    if self._VERBOSE:
      print(f"DEL  v3/{path} -- {resp.status_code}")
      if resp.status_code != 200:
        print(resp.text)
    return resp.json()


  def _sign_in(self, api_key, api_secret):
    resp = self._post(
      "developer/sign-in",
      {
        "apiKey": api_key,
        "apiSecret": api_secret
      }
    )
    self._sess.headers.update({
      "Authorization": f"Bearer {resp['token']}"
    })

  #################################################################
  # ACTIVITIES


  def list_activities(self):
    return self._get(f"activities")['activities']


  def update_activity(self, id, **new_values):
    return self._patch(f"activities/{id}", new_values)


  def archive_activity(self, id):
    return self._del(f"activities/{id}")

  #################################################################
  # DEVICES


  def list_devices(self):
    return self._get(f"devices")['devices']


  def set_active_device(self, device_id):
    resp = self._post(f"devices/{device_id}/activate")
    self._active_device = device_id
    return resp


  def release_active_device(self):
    if not self._active_device:
      raise Error("no active device")
    return self._post(f"devices/{self._active_device}/deactivate")


  def edit_device_name(self, device_id, name):
    return self._patch(f"devices/{device_id}", {"name": name})


  def forget_device(self, device_id):
    return self._del(f"devices/{device_id}")


  def disable_device(self, device_id):
    return self._post(f"devices/{device_id}/disable")


  def enable_device(self, device_id):
    return self._post(f"devices/{device_id}/enable")

  #################################################################
  # TRACKING


  def get_current_tracking(self):
    return self._get(f"tracking")["currentTracking"]


  def start_tracking(self, id): # no idea what the ID is here.
    return self._post(f"tracking/{id}/start")


  def edit_current_tracking(self, note, activity_id, started_at):
    return self._patch(f"tracking",
      {
        note:note,
        activity_id:activity_id,
        started_at:started_at,
      }
    )


  def stop_tracking(self):
    return self._post(f"tracking/stop")

  #################################################################
  # TIME ENTRIES


  def find_entries_in_range(self, start_dt, stop_dt):
    return self._get(f"time-entries/{_dump_datetime(start_dt)}/{_dump_datetime(stop_dt)}")['timeEntries']


  def create_entry(self, activity_id, start_dt, stop_dt, note_text):
    entry = {
      "activityId": activity_id,
      "startedAt": _dump_datetime(start_dt),
      "stoppedAt": _dump_datetime(stop_dt),
      "note": {"text" : note_text}
    }
    return self._post(f"time-entries", entry)


  def get_entry(self, entry_id):
    return self._get(f"time-entries/{entry_id}")


  def edit_entry(self, entry_id, activity_id=None, start_dt=None, stop_dt=None, note_text=None):
    entry_fields = {k:v for k, v in [
      ("activityId", activity_id),
      ("startedAt", start_dt and _dump_datetime(start_dt)),
      ("stoppedAt", stop_dt and _dump_datetime(stop_dt)),
      ("note", {"text" : note_text} if note_text else None)
      ] if v}
    return self._patch(f"time-entries/{entry_id}", entry_fields)


  def delete_entry(self, entry_id):
    return self._del(f"time-entries/{entry_id}")

  #################################################################
  # REPORTS


  def generate_report_csv(self, start_dt, end_dt, timezone=tzlocal.get_localzone().zone):
    return self._get(f"report/{_dump_datetime(start_dt)}/{_dump_datetime(end_dt)}?timezone={timezone}",
      return_text=True)


  def report_report_json(self, start_dt, end_dt):
    return self._get(f"report/data/{_dump_datetime(start_dt)}/{_dump_datetime(end_dt)}")

  #################################################################
  # TAGS AND MENTIONS


  def get_tags_and_mentions(self):
    return self._get(f"tags-and-mentions")


  def create_tag(self, key, label, scope, space_id):
    return self._post(f"tags", {
      "key": key,
      "label": label,
      "scope": scope,
      "space_id": space_id,
    })


  def update_tag(self, tag_id, key=None, label=None, scope=None, space_id=None):
    return self._patch(f"tags/{tag_id}",
      {k:v for k, v in ({
        ("key", key),
        ("label", label),
        ("scope", scope),
        ("space_id", space_id),
      }) if v}
    )


  def delete_tag(self, tag_id):
    return self._del(f"tags/{tag_id}")


  def create_mention(self, key, label, scope, space_id):
    return self._post(f"mentions", {
      "key": key,
      "label": label,
      "scope": scope,
      "space_id": space_id,
    })


  def update_mention(self, mention_id, key=None, label=None, scope=None, space_id=None):
    return self._patch(f"mentions/{mention_id}",
      {k:v for k, v in ({
        ("key", key),
        ("label", label),
        ("scope", scope),
        ("space_id", space_id),
      }) if v}
    )


  def delete_mention(self, mention_id):
    return self._del(f"mentions/{mention_id}")

  #################################################################
  # USER


  def me(self):
    return self._get(f"me")['data']


  def list_spaces(self):
    return self._get(f"space")['data']

  #################################################################
  # WEBHOOKS


  def list_webhook_events(self):
    """
      "timeEntryCreated","timeEntryUpdated","timeEntryDeleted",
      "trackingStarted","trackingStopped","trackingEdited","trackingCanceled"
    """
    return self._get(f"webhooks/event")


  def subscribe(self, event, target_url):
    return self._post(f"webhooks/subscription",
      {"event": event, "target_url": target_url}
      )


  def unsubscribe(self, subscription_id):
    return self._del(f"webhooks/subscription/{subscription_id}")


  def list_subscriptions(self):
    return self._get(f"webhooks/subscription")['subscriptions']


  def unsubscribe_all(self):
    return self._del(f"webhooks/subscription")


