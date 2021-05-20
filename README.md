# sdk-timeular-tools

a completely unofficial timeular python SDK and some simple utilities and notebooks

The Timeular v3 API docs can be found (here)[https://developers.timeular.com/].

## Usage

See the (notebooks)[./notebooks] directory for usage examples.

```
from timeular import timeular

with timeular.TimeularSession(API_KEY, API_SECRET) as ts:
    activities = ts.activities()
    # and so on...
```


### Methods available:

__activities__

```
  def list_activities()
  def update_activity(id, **new_values)
  def archive_activity(id)
```

__devices__

```
  def list_devices()
  def set_active_device(device_id)
  def release_active_device()
  def edit_device_name(device_id, name)
  def forget_device(device_id)
  def disable_device(device_id)
  def enable_device(device_id)
```

__tracking__

```
  def get_current_tracking()
  def start_tracking(id) # no idea what the ID is here.
  def edit_current_tracking(note, activity_id, started_at)
  def stop_tracking()
```

__entries__

```
  def find_entries_in_range(start_dt, stop_dt)
  def create_entry(activity_id, start_dt, stop_dt, note_text)
  def get_entry(entry_id)
  def edit_entry(entry_id, activity_id=None, start_dt=None, stop_dt=None, note_text=None)
  def delete_entry(entry_id)
```

__reports__

```
  def generate_report_csv(start_dt, end_dt, timezone=tzlocal.get_localzone().zone)
  def report_report_json(start_dt, end_dt)
```

__tags and mentions__

```
  def get_tags_and_mentions()
  def create_tag(key, label, scope, space_id)
  def update_tag(tag_id, key=None, label=None, scope=None, space_id=None)
  def delete_tag(tag_id)
  def create_mention(key, label, scope, space_id)
  def update_mention(mention_id, key=None, label=None, scope=None, space_id=None)
  def delete_mention(mention_id)
```

__user and group info__

```
  def me()
  def list_spaces()
```

__webhooks__

```
  def list_webhook_events()
  def subscribe(event, target_url)
  def unsubscribe(subscription_id)
  def list_subscriptions()
  def unsubscribe_all()
```