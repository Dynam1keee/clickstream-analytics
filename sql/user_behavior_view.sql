-- Create the USER_BEHAVIOR_VIEW view and split sessions into subsessions,
-- starting a new subsession when the gap between consecutive clicks exceeds 30 minutes.
-- For each subsession, calculate the total number of clicks, the number of unique
-- source and target pages, the session duration in minutes, and a bounce indicator
-- set to 1 when the subsession contains only one click.
CREATE OR REPLACE VIEW USER_BEHAVIOR_VIEW AS
WITH subsessions AS (
    SELECT
        SESSION_ID,
        CLICK_TIMESTAMP,
        SOURCE_URL,
        TARGET_URL,
        SUM(new_session_flag)
            OVER (PARTITION BY SESSION_ID ORDER BY CLICK_TIMESTAMP) AS subsession_id
    FROM (
        SELECT
            SESSION_ID,
            CLICK_TIMESTAMP,
            SOURCE_URL,
            TARGET_URL,
            CASE
                WHEN LAG(CLICK_TIMESTAMP) OVER (PARTITION BY SESSION_ID ORDER BY CLICK_TIMESTAMP) IS NULL THEN 1
                WHEN (CAST(CLICK_TIMESTAMP AS DATE) - CAST(LAG(CLICK_TIMESTAMP) OVER (PARTITION BY SESSION_ID ORDER BY CLICK_TIMESTAMP) AS DATE)) * 24*60 > 30 THEN 1
                ELSE 0
            END AS new_session_flag
        FROM MY_SCHEMA.CLICKS
    )
)
SELECT
    SESSION_ID,
    subsession_id,
    COUNT(*) AS total_clicks,
    COUNT(DISTINCT SOURCE_URL) AS unique_sources,
    COUNT(DISTINCT TARGET_URL) AS unique_targets,
    ROUND(((CAST(MAX(CLICK_TIMESTAMP) AS DATE) - CAST(MIN(CLICK_TIMESTAMP) AS DATE)) * 24 * 60), 2) AS session_duration_minutes,
    CASE WHEN COUNT(*) = 1 THEN 1 ELSE 0 END AS bounce
FROM subsessions
GROUP BY SESSION_ID, subsession_id;