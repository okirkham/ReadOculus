import pandas as pd
import numpy as np
import os

def main():
    basepath = r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06"
    combined_log_path = os.path.join(basepath, "data", "combined_log.csv")
    df = pd.read_csv(combined_log_path, encoding="utf-8", sep=',')

    # --- Heading segments ---
    heading_segments = [
        {"start": "2025-05-21 19:50:25.000", "end": "2025-05-21 19:51:08.000", "heading": 180}
    ]

    # --- Compute distance ---
    processed_df = compute_distance(df, heading_segments)

    # --- Save output ---
    out_path = os.path.join(basepath, "data", "processed_combined_log.csv")
    processed_df.to_csv(out_path, mode='a', index=False)
    print("Processing complete. Processed data saved to:", out_path)

def compute_distance(df, heading_segments):
    # Assign heading based on timestamp ranges
    df['heading'] = None
    for seg in heading_segments:
        start = pd.to_datetime(seg['start'])
        end = pd.to_datetime(seg['end'])
        heading = seg['heading']
        df.loc[(df['timestamp'] >= start) & (df['timestamp'] < end), 'heading'] = heading

    df = df[df['heading'].notna()].copy()

    # Create unique timestamp DataFrame
    unique_ts_df = (
        df[['timestamp', 'velocity_forward (m/s)', 'velocity_right (m/s)', 'heading']]
        .drop_duplicates('timestamp')
        .sort_values('timestamp')
        .reset_index(drop=True)
    )

    unique_ts_df['delta_time'] = 0.0

    # Compute delta_time only within each heading segment
    for seg in heading_segments:
        start = pd.to_datetime(seg['start'])
        end = pd.to_datetime(seg['end'])
        mask = (unique_ts_df['timestamp'] >= start) & (unique_ts_df['timestamp'] < end)
        segment_df = unique_ts_df.loc[mask].copy()
        segment_df['delta_time'] = segment_df['timestamp'].diff().dt.total_seconds().fillna(0)
        unique_ts_df.loc[mask, 'delta_time'] = segment_df['delta_time']

    # Directional distances
    unique_ts_df['distance_forward'] = unique_ts_df['velocity_forward (m/s)'] * unique_ts_df['delta_time']
    unique_ts_df['distance_right'] = unique_ts_df['velocity_right (m/s)'] * unique_ts_df['delta_time']

    # Reverse for heading 180
    reverse_mask = unique_ts_df['heading'] == 180
    unique_ts_df.loc[reverse_mask, 'distance_forward'] *= -1
    unique_ts_df.loc[reverse_mask, 'distance_right'] *= -1

    # Segment-wise cumulative totals
    total_forward = []
    total_right = []
    fwd_sum = 0
    right_sum = 0

    for i in range(len(unique_ts_df)):
        fwd_sum += unique_ts_df.loc[i, 'distance_forward']
        right_sum += unique_ts_df.loc[i, 'distance_right']
        total_forward.append(fwd_sum)
        total_right.append(right_sum)

    unique_ts_df['total_forward'] = total_forward
    unique_ts_df['total_right'] = total_right
    unique_ts_df['distance_traveled'] = np.sqrt(
        unique_ts_df['distance_forward']**2 + unique_ts_df['distance_right']**2
    )
    unique_ts_df['total_distance'] = unique_ts_df['distance_traveled'].cumsum()

    # Merge back
    result_df = df.merge(
        unique_ts_df[['timestamp', 'heading', 'delta_time', 'distance_forward', 'distance_right',
                      'distance_traveled', 'total_forward', 'total_right', 'total_distance']],
        on='timestamp',
        how='left'
    )

    return result_df

if __name__ == "__main__":
    main()