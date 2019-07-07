
-- create database, and raw_symbols table; and load from csv files

create database finance;
use finance;

CREATE TABLE `raw_symbols` (
  `symbol` varchar(10) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_sale` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `market_cap` varchar(16) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ipo_year` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sector` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `industry` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `summary_quote` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  KEY `symbol_index` (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci

SHOW VARIABLES LIKE 'local_infile';

SET GLOBAL local_infile = 1;

LOAD DATA local INFILE '/Users/yanzhi_bai/repos/list2/companylist.csv'  INTO TABLE raw_symbols  FIELDS TERMINATED BY ',' ENCLOSED BY '"'  LINES TERMINATED BY '\n'  IGNORE 1 ROWS;
--or 
LOAD DATA local INFILE '/Users/baifriend/repos/list2/metadata/companylist-2.csv'  INTO TABLE raw_symbols  FIELDS TERMINATED BY ',' ENCLOSED BY '"'  LINES TERMINATED BY '\n'  IGNORE 1 ROWS;


-- list_symbols table, and insert data 

CREATE TABLE `list2_symbols` (
  `symbol` varchar(10) NOT NULL DEFAULT '',
  `sector` varchar(30) DEFAULT NULL,  
  `industry` varchar(50) DEFAULT NULL,

  `market_cap_m` float DEFAULT NULL,  -- relative fixed above

  `last_close` float DEFAULT NULL,  
  `ma_131` float DEFAULT NULL,  
   price_ratio float,
   price_percentage float,

   psr float,
   psr_percentage float,

   earning_1 float,
   earning_2 float,
   earning_3 float,
   earning_4 float,
   earning_5 float,  -- most recent
   earning_growth float,
   earning_growth_percentage float,

   exception varchar(100),

   updated_at datetime,

  KEY `symbol_index` (`symbol`)
) 

insert into list2_symbols(symbol,sector,industry,market_cap_m)
select  
    symbol,
    sector,
    industry,
    CASE
      WHEN market_cap like '%M' THEN cast(TRIM(LEADING '$' FROM market_cap) as decimal(20,3))
      WHEN market_cap like '%B' THEN cast(TRIM(LEADING '$' FROM market_cap) as decimal(20,3))*1000
      ELSE cast(TRIM(LEADING '$' FROM market_cap) as decimal(20,3))/1000000
    END as market_cap_m
from raw_symbols
where 
sector<>'n/a' and industry<>'n/a' and market_cap<>'n/a'


--total 4933 rows
--note: decimal(total digits, after dot digits)


-- steps:
-- 1, dump 5k symbols out
    -- add this in if security reason:
    --~/repos/list2(master ✗) sudo cat  /etc/my.cnf
    --[mysqld]
    --secure_file_priv  = ''
    SELECT symbol FROM list2_symbols
    INTO OUTFILE '/Users/baifriend/repos/list2/symbols.csv' FIELDS TERMINATED BY ','  LINES TERMINATED BY '\n';

-- Optional
-- 1.1, transfer downloaded data among computers, export into a file:
    select * from list2_symbols into OUTFILE '/Users/baifriend/repos/list2/list_fundamental.csv' 
    FIELDS TERMINATED BY ','  LINES TERMINATED BY '\n';
-- 1.2, load back to table
    LOAD DATA local INFILE '/Users/yanzhi_bai/repos/list2/list_fundamental.csv'  INTO TABLE list2_symbols  
    FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';


--2, get price data in (from Amibroker)
    create temporary table price_temp (symbol varchar(10),  `last_close` float,   
    `ma_131` float DEFAULT NULL, price_ratio float);
    
    LOAD DATA local INFILE '/Users/yanzhi_bai/repos/list2/2019-07-06_LIST2.txt'  INTO TABLE price_temp  
    FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';

    update list2_symbols INNER JOIN  price_temp on price_temp.symbol = list2_symbols.symbol 
    set list2_symbols.last_close=price_temp.last_close, 
    list2_symbols.ma_131=price_temp.ma_131, 
    list2_symbols.price_ratio=price_temp.price_ratio;

    drop temporary table price_temp;
    
-- 3, calculate ratios, and update percentages data


-- 4, sort by percentage, and query.

--SELECT *, price/(erecent+emid3) as pe
--FROM `list2_`
--where cegrow>=90 and cpratio>=90 and cpps<=30


