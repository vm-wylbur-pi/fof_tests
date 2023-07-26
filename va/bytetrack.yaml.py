# Ultralytics YOLO 🚀, AGPL-3.0 license
# Default YOLO tracker settings for ByteTrack tracker https://github.com/ifzhang/ByteTrack

tracker_type: bytetrack  # tracker type, ['botsort', 'bytetrack']
track_high_thresh: 0.1  # threshold for the first association
track_low_thresh: 0.01  # threshold for the second association
new_track_thresh: 0.6  # threshold for init new track if the detection does not match any tracks
track_buffer: 30  # buffer to calculate the time when to remove tracks
match_thresh: 0.8  # threshold for matching tracks
# min_box_area: 10  # threshold for min box areas(for tracker evaluation, not used for now)
# mot20: False  # for tracker evaluation(not used for now)