with source_rows as (
    SELECT row_count FROM `{{ dataset }}.{{ schema }}.__TABLES__` where table_id = '{{table}}'
),
target_rows as (
    SELECT row_count FROM `{{ dataset }}.{{ compare_schema }}.__TABLES__` where table_id = '{{table}}'
)
SELECT
        source_rows.row_count as source_row_count,
        target_rows.row_count as target_row_count,
        source_rows.row_count - target_rows.row_count as diff,
        CASE
            WHEN target_rows.row_count > 0
                THEN abs(1.0 * (target_rows.row_count - source_rows.row_count))/NULLIF(target_rows.row_count, 0)
            WHEN target_rows.row_count = source_rows.row_count
                THEN 0
            ELSE
                1
        END
        AS diff_percent
    from source_rows, target_rows
