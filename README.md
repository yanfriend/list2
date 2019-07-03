# list2

the app include
- stock symbols (true stock)
- crawler to pull earning growth, price/sales ratios and save to mysql
- price relative strength (price/131 moving average)
- sort according to percentage

geckodriver download:
https://github.com/mozilla/geckodriver/releases

refer:
DROP TABLE IF EXISTS `alldata`;
CREATE TABLE `alldata` (
  `symbol` varchar(10) NOT NULL default '',
  `price` float unsigned NOT NULL default '0',
  `pratio` float unsigned NOT NULL default '0',
  `pps` float NOT NULL default '0',
  `egrow` float NOT NULL default '-9.9',
  `erecent` float NOT NULL default '0',
  `emid3` float NOT NULL default '0',
  `eremote` float NOT NULL default '0',
  `cpratio` int(5) unsigned NOT NULL default '0',
  `cpps` int(5) unsigned NOT NULL default '0',
  `cegrow` int(5) unsigned NOT NULL default '0',
  `grab_date` date NOT NULL default '0000-00-00'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
