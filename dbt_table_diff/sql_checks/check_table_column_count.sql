with source_columns as (SELECT distinct column_name as column_name
                        FROM `{{ dataset }}.{{ schema }}.INFORMATION_SCHEMA.COLUMNS`
                        where table_name = '{{table}}'),
     target_columns as (SELECT distinct column_name as column_name
                        FROM `{{ dataset }}.{{ compare_schema }}.INFORMATION_SCHEMA.COLUMNS`
                        where table_name = '{{table}}')
    (SELECT "Column only found in Prod" as type, column_name
     FROM target_columns
     EXCEPT
     DISTINCT
     SELECT "Column only found in Prod" as type, column_name
     from source_columns)

UNION ALL

(SELECT "Column only found in Dev" as type, column_name
 FROM source_columns
 EXCEPT
 DISTINCT
 SELECT "Column only found in Dev" as type, column_name
 from target_columns)