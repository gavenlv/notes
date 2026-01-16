-- 日期工具宏测试
-- 测试日期相关的宏功能

-- 测试 format_date 宏
{% set test_date = "'2023-12-25'" %}
{% set formatted_date = format_date(test_date, 'YYYY-MM-DD') %}

select 
    {{ formatted_date }} as formatted_result,
    case 
        when {{ formatted_date }} = '2023-12-25' then 'PASS'
        else 'FAIL'
    end as format_date_test

union all

-- 测试 date_diff 宏
{% set date1 = "'2023-01-01'" %}
{% set date2 = "'2023-12-31'" %}
{% set day_diff = date_diff(date1, date2, 'day') %}

select 
    {{ day_diff }} as day_difference,
    case 
        when {{ day_diff }} = 364 then 'PASS'
        else 'FAIL'
    end as date_diff_test

union all

-- 测试 add_days 宏
{% set original_date = "'2023-01-01'" %}
{% set new_date = add_days(original_date, 30) %}

select 
    {{ new_date }} as new_date_result,
    case 
        when {{ new_date }} = dateadd('day', 30, '2023-01-01') then 'PASS'
        else 'FAIL'
    end as add_days_test

union all

-- 测试 is_weekend 宏
{% set weekend_date = "'2023-12-30'" %}  -- 周六
{% set weekday_date = "'2023-12-29'" %}  -- 周五

select 
    {{ is_weekend(weekend_date) }} as is_weekend_result,
    case 
        when {{ is_weekend(weekend_date) }} = true then 'PASS'
        else 'FAIL'
    end as weekend_test

union all

select 
    {{ is_weekend(weekday_date) }} as is_weekday_result,
    case 
        when {{ is_weekend(weekday_date) }} = false then 'PASS'
        else 'FAIL'
    end as weekday_test

union all

-- 测试 business_days_between 宏
{% set start_date = "'2023-12-25'" %}  -- 周一
{% set end_date = "'2023-12-29'" %}    -- 周五
{% set business_days = business_days_between(start_date, end_date) %}

select 
    {{ business_days }} as business_days_result,
    case 
        when {{ business_days }} = 4 then 'PASS'
        else 'FAIL'
    end as business_days_test

union all

-- 测试 age_in_years 宏
{% set birth_date = "'1990-01-01'" %}
{% set reference_date = "'2023-12-31'" %}
{% set age = age_in_years(birth_date, reference_date) %}

select 
    {{ age }} as age_result,
    case 
        when {{ age }} = 33 then 'PASS'
        else 'FAIL'
    end as age_test

union all

-- 测试 fiscal_year 宏
{% set test_date = "'2023-05-15'" %}  -- 5月，财年开始为4月
{% set fiscal_year = fiscal_year(test_date, 4) %}

select 
    {{ fiscal_year }} as fiscal_year_result,
    case 
        when {{ fiscal_year }} = 2023 then 'PASS'
        else 'FAIL'
    end as fiscal_year_test

union all

-- 测试 get_month_start 宏
{% set test_date = "'2023-12-25'" %}
{% set month_start = get_month_start(test_date) %}

select 
    {{ month_start }} as month_start_result,
    case 
        when {{ month_start }} = date_trunc('month', '2023-12-25') then 'PASS'
        else 'FAIL'
    end as month_start_test