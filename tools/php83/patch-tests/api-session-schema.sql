CREATE TABLE IF NOT EXISTS `invalid_session` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ks` varchar(300) DEFAULT NULL,
  `ks_valid_until` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `actions_limit` int(11) DEFAULT NULL,
  `type` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ks_index` (`ks`(255)),
  KEY `ks_valid_until_index` (`ks_valid_until`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
