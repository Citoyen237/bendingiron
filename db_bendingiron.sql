-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  sam. 30 août 2025 à 14:07
-- Version du serveur :  10.4.10-MariaDB
-- Version de PHP :  7.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `db_bendingiron`
--

-- --------------------------------------------------------

--
-- Structure de la table `archives_archives`
--

DROP TABLE IF EXISTS `archives_archives`;
CREATE TABLE IF NOT EXISTS `archives_archives` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `titre` varchar(255) NOT NULL,
  `file` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `type` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `archives_archives_user_id_671a3cff` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `archives_archives`
--

INSERT IGNORE INTO `archives_archives` (`id`, `titre`, `file`, `description`, `type`, `created_at`, `user_id`) VALUES
(14, 'Magni nulla dolor', 'archives/presentation_kayo.pdf', 'Qui temporibus ex mo', 'documents', '2025-08-19 02:04:31.841513', 1),
(15, 'Article 2', 'archives/logo.PNG', 'lonenknwnnk', 'images', '2025-08-19 11:47:16.100911', 1);

-- --------------------------------------------------------

--
-- Structure de la table `auth_app_customuser`
--

DROP TABLE IF EXISTS `auth_app_customuser`;
CREATE TABLE IF NOT EXISTS `auth_app_customuser` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone_number` varchar(200) NOT NULL,
  `is_partenaire` tinyint(1) NOT NULL,
  `email_verified` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `auth_app_customuser`
--

INSERT IGNORE INTO `auth_app_customuser` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `phone_number`, `is_partenaire`, `email_verified`) VALUES
(1, 'pbkdf2_sha256$720000$PaFnpXVyl8RSWv82YZSDdN$zBrjJvCOuaVPHgQc4491jsPTVBnxPHi0ypwaVakNUEU=', '2025-08-22 09:59:14.298075', 1, 'citoyen', 'ROMEO', 'NANA NANGMO', 'nanaromeo237@gmail.com', 1, 1, '2025-06-12 09:56:36.000000', '655927237', 1, 1),
(2, 'pbkdf2_sha256$720000$jMrcVYBCIiRbtsfMpArsWl$yOr+6RpJ8xGiqtGmw3kFpGLLwbAarQnx/82N2z0TjZ4=', '2025-07-12 13:56:36.298025', 1, 'YMELE', 'YMELE', 'Parfait', 'ymeleparfait@gmail.com', 1, 1, '2025-07-12 13:54:59.221970', '677951855', 1, 1),
(6, 'pbkdf2_sha256$720000$HvXRMErJeYC36i9C3AwGEL$/dljxHC4wyT/GEfCZfHpW3rGVq0E0DU7Ztp8CHHdndA=', '2025-08-22 09:48:40.077620', 0, 'MacKenzie', 'MacKenzie', 'Dunlap', 'bendingiron.info@gmail.com', 0, 1, '2025-08-21 11:38:27.378430', '+1 (957) 972-2836', 0, 1),
(7, 'pbkdf2_sha256$720000$O6KHkPo0GZw3rNIJiT9hAR$gAVj0iAj8GiP3gsOlfv5nTWIf/4Ojzbk3e5Ts4ocZKU=', NULL, 0, 'Rahim', 'Rahim', 'Graves', 'kawe@mailinator.com', 0, 1, '2025-08-21 12:39:31.534570', '+1 (183) 178-9553', 0, 0);

-- --------------------------------------------------------

--
-- Structure de la table `auth_app_customuser_groups`
--

DROP TABLE IF EXISTS `auth_app_customuser_groups`;
CREATE TABLE IF NOT EXISTS `auth_app_customuser_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_app_customuser_groups_customuser_id_group_id_eef898f9_uniq` (`customuser_id`,`group_id`),
  KEY `auth_app_customuser_groups_customuser_id_cfa7c414` (`customuser_id`),
  KEY `auth_app_customuser_groups_group_id_951c60f2` (`group_id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `auth_app_customuser_groups`
--

INSERT IGNORE INTO `auth_app_customuser_groups` (`id`, `customuser_id`, `group_id`) VALUES
(9, 2, 3),
(11, 1, 3),
(15, 6, 1);

-- --------------------------------------------------------

--
-- Structure de la table `auth_app_customuser_user_permissions`
--

DROP TABLE IF EXISTS `auth_app_customuser_user_permissions`;
CREATE TABLE IF NOT EXISTS `auth_app_customuser_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_app_customuser_user_customuser_id_permission_fd51d15d_uniq` (`customuser_id`,`permission_id`),
  KEY `auth_app_customuser_user_permissions_customuser_id_fdf7c76a` (`customuser_id`),
  KEY `auth_app_customuser_user_permissions_permission_id_0ed30c88` (`permission_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `auth_app_customuser_user_permissions`
--

INSERT IGNORE INTO `auth_app_customuser_user_permissions` (`id`, `customuser_id`, `permission_id`) VALUES
(1, 1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `auth_group`
--

INSERT IGNORE INTO `auth_group` (`id`, `name`) VALUES
(1, 'simple'),
(2, 'admin'),
(3, 'superadmin'),
(4, 'partenaire');

-- --------------------------------------------------------

--
-- Structure de la table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_group_id_b120cbf9` (`group_id`),
  KEY `auth_group_permissions_permission_id_84c5c92e` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id_2f476e4b` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=241 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `auth_permission`
--

INSERT IGNORE INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(117, 'Can add log entry', 1, 'add_logentry'),
(118, 'Can change log entry', 1, 'change_logentry'),
(119, 'Can delete log entry', 1, 'delete_logentry'),
(120, 'Can view log entry', 1, 'view_logentry'),
(121, 'Can add permission', 2, 'add_permission'),
(122, 'Can change permission', 2, 'change_permission'),
(123, 'Can delete permission', 2, 'delete_permission'),
(124, 'Can view permission', 2, 'view_permission'),
(125, 'Can add group', 3, 'add_group'),
(126, 'Can change group', 3, 'change_group'),
(127, 'Can delete group', 3, 'delete_group'),
(128, 'Can view group', 3, 'view_group'),
(129, 'Can add content type', 4, 'add_contenttype'),
(130, 'Can change content type', 4, 'change_contenttype'),
(131, 'Can delete content type', 4, 'delete_contenttype'),
(132, 'Can view content type', 4, 'view_contenttype'),
(133, 'Can add session', 5, 'add_session'),
(134, 'Can change session', 5, 'change_session'),
(135, 'Can delete session', 5, 'delete_session'),
(136, 'Can view session', 5, 'view_session'),
(137, 'Can add temoignage', 6, 'add_temoignage'),
(138, 'Can change temoignage', 6, 'change_temoignage'),
(139, 'Can delete temoignage', 6, 'delete_temoignage'),
(140, 'Can view temoignage', 6, 'view_temoignage'),
(141, 'Can add user', 7, 'add_customuser'),
(142, 'Can change user', 7, 'change_customuser'),
(143, 'Can delete user', 7, 'delete_customuser'),
(144, 'Can view user', 7, 'view_customuser'),
(145, 'Can add fer', 8, 'add_fer'),
(146, 'Can change fer', 8, 'change_fer'),
(147, 'Can delete fer', 8, 'delete_fer'),
(148, 'Can view fer', 8, 'view_fer'),
(149, 'Can add mouvement', 9, 'add_mouvement'),
(150, 'Can change mouvement', 9, 'change_mouvement'),
(151, 'Can delete mouvement', 9, 'delete_mouvement'),
(152, 'Can view mouvement', 9, 'view_mouvement'),
(153, 'Can add contact file', 10, 'add_contactfile'),
(154, 'Can change contact file', 10, 'change_contactfile'),
(155, 'Can delete contact file', 10, 'delete_contactfile'),
(156, 'Can view contact file', 10, 'view_contactfile'),
(157, 'Can add contact', 11, 'add_contact'),
(158, 'Can change contact', 11, 'change_contact'),
(159, 'Can delete contact', 11, 'delete_contact'),
(160, 'Can view contact', 11, 'view_contact'),
(161, 'Can add categorie', 12, 'add_categorie'),
(162, 'Can change categorie', 12, 'change_categorie'),
(163, 'Can delete categorie', 12, 'delete_categorie'),
(164, 'Can view categorie', 12, 'view_categorie'),
(165, 'Can add produit', 13, 'add_produit'),
(166, 'Can change produit', 13, 'change_produit'),
(167, 'Can delete produit', 13, 'delete_produit'),
(168, 'Can view produit', 13, 'view_produit'),
(169, 'Can add cart item', 14, 'add_cartitem'),
(170, 'Can change cart item', 14, 'change_cartitem'),
(171, 'Can delete cart item', 14, 'delete_cartitem'),
(172, 'Can view cart item', 14, 'view_cartitem'),
(173, 'Can add cart', 15, 'add_cart'),
(174, 'Can change cart', 15, 'change_cart'),
(175, 'Can delete cart', 15, 'delete_cart'),
(176, 'Can view cart', 15, 'view_cart'),
(177, 'Can add order', 16, 'add_order'),
(178, 'Can change order', 16, 'change_order'),
(179, 'Can delete order', 16, 'delete_order'),
(180, 'Can view order', 16, 'view_order'),
(181, 'Can add order item', 17, 'add_orderitem'),
(182, 'Can change order item', 17, 'change_orderitem'),
(183, 'Can delete order item', 17, 'delete_orderitem'),
(184, 'Can view order item', 17, 'view_orderitem'),
(185, 'Can add traiment', 18, 'add_traiment'),
(186, 'Can change traiment', 18, 'change_traiment'),
(187, 'Can delete traiment', 18, 'delete_traiment'),
(188, 'Can view traiment', 18, 'view_traiment'),
(189, 'Can add fer price', 19, 'add_ferprice'),
(190, 'Can change fer price', 19, 'change_ferprice'),
(191, 'Can delete fer price', 19, 'delete_ferprice'),
(192, 'Can view fer price', 19, 'view_ferprice'),
(193, 'Can add partenariats', 20, 'add_partenariats'),
(194, 'Can change partenariats', 20, 'change_partenariats'),
(195, 'Can delete partenariats', 20, 'delete_partenariats'),
(196, 'Can view partenariats', 20, 'view_partenariats'),
(197, 'Can add projet', 21, 'add_projet'),
(198, 'Can change projet', 21, 'change_projet'),
(199, 'Can delete projet', 21, 'delete_projet'),
(200, 'Can view projet', 21, 'view_projet'),
(201, 'Can add projet item', 22, 'add_projetitem'),
(202, 'Can change projet item', 22, 'change_projetitem'),
(203, 'Can delete projet item', 22, 'delete_projetitem'),
(204, 'Can view projet item', 22, 'view_projetitem'),
(205, 'Can add paimenent projet', 23, 'add_paimenentprojet'),
(206, 'Can change paimenent projet', 23, 'change_paimenentprojet'),
(207, 'Can delete paimenent projet', 23, 'delete_paimenentprojet'),
(208, 'Can view paimenent projet', 23, 'view_paimenentprojet'),
(209, 'Can add projet order', 24, 'add_projetorder'),
(210, 'Can change projet order', 24, 'change_projetorder'),
(211, 'Can delete projet order', 24, 'delete_projetorder'),
(212, 'Can view projet order', 24, 'view_projetorder'),
(213, 'Can add paiement projet', 25, 'add_paiementprojet'),
(214, 'Can change paiement projet', 25, 'change_paiementprojet'),
(215, 'Can delete paiement projet', 25, 'delete_paiementprojet'),
(216, 'Can view paiement projet', 25, 'view_paiementprojet'),
(217, 'Can add projet order item', 26, 'add_projetorderitem'),
(218, 'Can change projet order item', 26, 'change_projetorderitem'),
(219, 'Can delete projet order item', 26, 'delete_projetorderitem'),
(220, 'Can view projet order item', 26, 'view_projetorderitem'),
(221, 'Can add traiment order', 27, 'add_traimentorder'),
(222, 'Can change traiment order', 27, 'change_traimentorder'),
(223, 'Can delete traiment order', 27, 'delete_traimentorder'),
(224, 'Can view traiment order', 27, 'view_traimentorder'),
(225, 'Can add order user info', 28, 'add_orderuserinfo'),
(226, 'Can change order user info', 28, 'change_orderuserinfo'),
(227, 'Can delete order user info', 28, 'delete_orderuserinfo'),
(228, 'Can view order user info', 28, 'view_orderuserinfo'),
(229, 'Can add payment', 29, 'add_payment'),
(230, 'Can change payment', 29, 'change_payment'),
(231, 'Can delete payment', 29, 'delete_payment'),
(232, 'Can view payment', 29, 'view_payment'),
(233, 'Can add code promo', 30, 'add_codepromo'),
(234, 'Can change code promo', 30, 'change_codepromo'),
(235, 'Can delete code promo', 30, 'delete_codepromo'),
(236, 'Can view code promo', 30, 'view_codepromo'),
(237, 'Can add archives', 31, 'add_archives'),
(238, 'Can change archives', 31, 'change_archives'),
(239, 'Can delete archives', 31, 'delete_archives'),
(240, 'Can view archives', 31, 'view_archives');

-- --------------------------------------------------------

--
-- Structure de la table `contact_contact`
--

DROP TABLE IF EXISTS `contact_contact`;
CREATE TABLE IF NOT EXISTS `contact_contact` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `nom` varchar(250) NOT NULL,
  `telephone` varchar(250) NOT NULL,
  `message` longtext NOT NULL,
  `type` varchar(50) NOT NULL,
  `reponse` longtext DEFAULT NULL,
  `is_read` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `file` varchar(100) DEFAULT NULL,
  `file_response` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `contact_contact`
--

INSERT IGNORE INTO `contact_contact` (`id`, `email`, `nom`, `telephone`, `message`, `type`, `reponse`, `is_read`, `created_at`, `updated_at`, `file`, `file_response`) VALUES
(1, 'jaricag@mailinator.com', 'Et asperiores qui et sunt eligendi recusandae Velit consequatur', '+1 (883) 841-3806', 'Dignissimos perspici', 'reclamation', NULL, 0, '2025-06-16 19:26:29.591033', '2025-06-16 19:26:29.591033', NULL, NULL),
(2, 'bujyvasi@mailinator.com', 'Aut debitis accusantium cillum at natus nostrum exercitationem officiis nihil dicta', '+1 (243) 427-8829', 'Optio esse quae nes', 'autre', NULL, 0, '2025-06-16 19:30:53.462728', '2025-06-16 19:30:53.462728', NULL, NULL),
(3, 'zure@mailinator.com', 'Nostrud amet laboris illo adipisci quia ea obcaecati et neque asperiores sit et', '+1 (241) 479-5627', 'Illo ad dolores veni', 'autre', NULL, 0, '2025-06-16 20:03:28.150636', '2025-06-16 20:03:28.155628', NULL, NULL),
(4, 'cagisufel@mailinator.com', 'Sit ut quasi quis sed et obcaecati non sunt adipisicing sit esse pariatur Atque molestiae excepturi officiis omnis debitis quia', '+1 (238) 448-8088', 'Eius delectus aut p', 'autre', NULL, 0, '2025-06-16 20:15:40.930104', '2025-06-16 20:15:40.930104', '', NULL),
(5, 'mizyxo@mailinator.com', 'Quia suscipit cum qui inventore eu asperiores vero est et ipsa minus neque', '+1 (421) 831-1918', 'Voluptatem in volupt', 'renseignements', NULL, 0, '2025-06-16 20:27:30.499225', '2025-06-16 20:27:30.499225', '', NULL),
(6, 'coby@mailinator.com', 'Eum consequuntur nobis dolores ex odit qui consequat Voluptatum est placeat esse laboriosam dignissimos dolorem harum sed adipisicing', '+1 (804) 149-1328', 'Dolor cupiditate dol', 'renseignements', '', 0, '2025-06-16 20:31:43.180645', '2025-06-16 20:31:43.180645', '', NULL),
(7, 'sijuviru@mailinator.com', 'Molestiae officia quos natus sunt impedit proident dolorum culpa quos inventore non in sapiente earum quasi sunt', '+1 (694) 798-2913', 'Consequatur Sunt es', 'devis', '', 1, '2025-06-16 20:37:24.565216', '2025-06-17 18:55:59.134481', 'contacts/files/contexte.pdf', ''),
(8, 'vepuwyri@mailinator.com', 'Est irure aspernatur incididunt perspiciatis eveniet unde fuga Distinctio Illum corrupti iure qui sint quia ut doloremque', '+1 (437) 562-6815', 'Ut quisquam totam ut', 'autre', NULL, 1, '2025-06-16 20:42:55.332568', '2025-06-17 07:17:12.479720', '', NULL),
(9, 'nanaromeo237@gmail.com', 'Proident delectus laboriosam sit unde earum cumque maxime sint aut labore atque voluptatibus nihil quia dolore dolorem', '+1 (114) 731-7597', 'Ut explicabo Deseru', 'renseignements', '', 1, '2025-06-16 20:56:47.524421', '2025-06-17 19:15:00.313211', 'contacts/files/contexte_M0QfchJ.pdf', 'contacts/files/COUVERTURE_SOUTENANCE__XnnFPgv.pdf'),
(10, 'puga@mailinator.com', 'Qui do sit et quasi dolor voluptatem inventore ipsam et et dolor ut consequatur nisi ea', '+1 (361) 611-5451', 'Dignissimos qui ipsu', 'renseignements', NULL, 0, '2025-06-17 23:20:49.805952', '2025-06-17 23:20:49.805952', '', ''),
(11, 'pike@mailinator.com', 'Iste in ullamco delectus culpa vero voluptatem', '+1 (346) 281-1826', 'Hic a dolorum quo es', 'devis', NULL, 0, '2025-06-17 23:29:19.348942', '2025-06-17 23:29:19.348942', '', ''),
(12, 'kemys@mailinator.com', 'Ut mollit non nostrud fugit et enim quo ut incidunt suscipit earum quas nulla delectus et laudantium tenetur praesentium qui', '+1 (234) 818-6732', 'Magna velit soluta o', 'devis', NULL, 1, '2025-06-17 23:45:59.552736', '2025-07-14 12:07:23.270259', '', ''),
(13, 'fucebo@mailinator.com', 'Ratione deserunt dolores exercitation non eos alias tenetur occaecat tempora qui', '+1 (803) 567-6755', 'Sunt qui nobis earu', 'autre', NULL, 0, '2025-06-17 23:47:29.294540', '2025-06-17 23:47:29.294540', '', ''),
(14, 'kopazizug@mailinator.com', 'Quia fugiat eu in ab officia voluptatum consectetur', '+1 (919) 913-6871', 'Quasi porro distinct', 'devis', NULL, 0, '2025-06-18 00:04:11.428768', '2025-06-18 00:04:11.428768', '', ''),
(15, 'temagumydy@mailinator.com', 'Non autem earum aut qui doloremque', '+1 (868) 569-5104', 'Voluptate deserunt s', 'autre', NULL, 1, '2025-06-18 00:07:30.304581', '2025-07-12 15:13:53.509233', '', ''),
(16, 'dfmacinfo@gmail.com', 'Necessitatibus optio aliquip dolorem quia nulla quo nostrud amet odit elit veritatis fuga Non modi in non culpa ex eaque', '+1 (304) 143-3973', 'Odit pariatur Conse', 'devis', 'test', 1, '2025-06-22 10:08:33.006131', '2025-06-22 10:12:50.442120', 'contacts/files/contexte_CBITwzB.pdf', 'contacts/files/COUVERTURE_SOUTENANCE__ArzUYbz.pdf');

-- --------------------------------------------------------

--
-- Structure de la table `contact_contactfile`
--

DROP TABLE IF EXISTS `contact_contactfile`;
CREATE TABLE IF NOT EXISTS `contact_contactfile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `contact_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `contact_contactfile_contact_id_0453d445` (`contact_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=177 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `django_admin_log`
--

INSERT IGNORE INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-06-13 15:51:56.052704', '1', 'simple', 1, '[{`added`: {}}]', 3, 1),
(2, '2025-06-13 15:52:03.925869', '2', 'admin', 1, '[{`added`: {}}]', 3, 1),
(3, '2025-06-13 15:52:35.157108', '3', 'superadmin', 1, '[{`added`: {}}]', 3, 1),
(4, '2025-06-13 15:57:32.682063', '1', 'nanaromeo237@gmail.com', 2, '[{`changed`: {`fields`: [`First name`, `Last name`, `Phone number`, `Groups`, `User permissions`]}}]', 7, 1),
(5, '2025-06-13 19:40:32.198156', '4', 'partenaire', 1, '[{`added`: {}}]', 3, 1),
(6, '2025-06-16 11:51:55.341296', '1', 'CINTRAGE DU FER A BETON', 1, '[{`added`: {}}]', 12, 1),
(7, '2025-06-16 11:52:40.597884', '2', 'CINTRAGE DU FER ROND', 1, '[{`added`: {}}]', 12, 1),
(8, '2025-06-16 11:53:00.862588', '3', 'QUICAILLERIE', 1, '[{`added`: {}}]', 12, 1),
(9, '2025-06-16 11:56:54.395787', '1', 'Produit object (1)', 1, '[{`added`: {}}]', 13, 1),
(10, '2025-06-16 12:42:46.685226', '2', 'Produit object (2)', 1, '[{`added`: {}}]', 13, 1),
(11, '2025-06-16 13:22:09.669113', '1', 'Produit object (1)', 2, '[{`changed`: {`fields`: [`Sous categorie`]}}]', 13, 1),
(12, '2025-06-16 13:24:44.074669', '1', 'Produit object (1)', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`, `Image sous categorie`, `Name page`, `Description`]}}]', 13, 1),
(13, '2025-06-16 20:31:43.189279', '6', 'coby@mailinator.com', 1, '[{`added`: {}}]', 11, 1),
(14, '2025-06-16 20:37:24.603179', '7', 'sijuviru@mailinator.com', 1, '[{`added`: {}}]', 11, 1),
(15, '2025-06-20 11:10:30.479721', '1', 'nanaromeo237@gmail.com - 27900.00', 2, '[{`changed`: {`fields`: [`Statut`]}}]', 16, 1),
(16, '2025-06-20 11:10:55.685618', '1', 'nanaromeo237@gmail.com - 27900.00', 2, '[{`changed`: {`fields`: [`Statut`]}}]', 16, 1),
(17, '2025-06-20 11:35:28.254935', '1', 'nanaromeo237@gmail.com - 27900.00-en_attente', 1, '[{`added`: {}}]', 18, 1),
(18, '2025-06-20 11:39:55.352822', '2', 'nanaromeo237@gmail.com - 27900.00-pret_pour_livraison', 1, '[{`added`: {}}]', 18, 1),
(19, '2025-06-20 13:16:07.653939', '2', 'nanaromeo237@gmail.com - 27900.00-pret_pour_livraison', 3, '', 18, 1),
(20, '2025-06-22 09:49:15.428689', '5', 'NANA NANGMO, ROMEO - 27900.00-solde_facture', 3, '', 18, 1),
(21, '2025-06-22 10:03:34.246944', '2', 'fils attache', 3, '', 13, 1),
(22, '2025-06-22 10:03:40.494779', '1', 'cadre carre', 3, '', 13, 1),
(23, '2025-06-22 10:10:49.803714', '16', 'dfmacinfo@gmail.com', 2, '[{`changed`: {`fields`: [`Email`]}}]', 11, 1),
(24, '2025-06-22 10:31:51.792231', '2', 'NANA NANGMO, ROMEO - 0', 3, '', 16, 1),
(25, '2025-06-22 10:31:58.974808', '1', 'NANA NANGMO, ROMEO - 0', 3, '', 16, 1),
(26, '2025-06-22 12:23:11.693332', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(27, '2025-06-22 12:24:18.750344', '26', 'ancrage en forme de crochet', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(28, '2025-06-22 12:24:41.975392', '26', 'Ancrage en forme de crochet', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(29, '2025-06-22 12:25:16.976945', '25', 'Ancrage en forme de crosse', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(30, '2025-06-22 12:26:07.481575', '24', 'Ancrage simple', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(31, '2025-06-22 12:26:53.755563', '23', 'Ancrage forme L', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(32, '2025-06-22 12:30:31.936537', '22', 'Ancrage forme J', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`, `Description`]}}]', 13, 1),
(33, '2025-06-22 12:35:54.531482', '21', 'etrier a fond triangulaire', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(34, '2025-06-22 12:41:28.557371', '20', 'etrier a une seul branche a fond droit', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(35, '2025-06-22 12:41:53.514249', '19', 'etrier a fond droit', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(36, '2025-06-22 12:42:30.347771', '18', 'etrier a une seul branche a fond circulaire', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(37, '2025-06-22 12:43:04.633061', '17', 'etrier a fond circulaire', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(38, '2025-06-22 12:46:14.978203', '16', 'barre coude aux deux extremites', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(39, '2025-06-22 12:46:59.496526', '15', 'barre coude a une extremite', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(40, '2025-06-22 12:47:56.894643', '14', 'barre droite', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(41, '2025-06-22 12:49:38.137816', '13', 'cintrage du crochet', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(42, '2025-06-22 12:50:09.537875', '12', 'cintrage pince', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(43, '2025-06-22 12:50:49.261040', '11', 'cintrage T economique', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(44, '2025-06-22 12:52:05.322341', '10', 'cintrage du U ferme', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(45, '2025-06-22 12:52:54.615164', '9', 'cintrage du U ouvert', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(46, '2025-06-22 12:54:26.761421', '8', 'cintrage en U', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(47, '2025-06-22 12:54:50.613484', '7', 'cintrage en T', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(48, '2025-06-22 12:56:19.563543', '6', 'cintrage de l\'etrier', 2, '[{`changed`: {`fields`: [`Nom`, `Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(49, '2025-06-22 12:57:45.397634', '10', 'cintrage en U ferme', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(50, '2025-06-22 12:57:58.802544', '9', 'cintrage en U ouvert', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(51, '2025-06-22 12:58:17.547736', '11', 'cintrage en T economique', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(52, '2025-06-22 13:13:46.318895', '12', 'cintrage de la pince', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(53, '2025-06-22 13:23:30.934327', '2', 'fils attache', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(54, '2025-06-22 13:33:10.840277', '28', 'fer a beton de 12m', 1, '[{`added`: {}}]', 13, 1),
(55, '2025-06-22 13:59:14.032708', '28', 'fer a beton de 12m', 2, '[{`changed`: {`fields`: [`Imageshop2d`]}}]', 13, 1),
(56, '2025-06-22 14:05:36.927949', '29', 'Ecrou', 1, '[{`added`: {}}]', 13, 1),
(57, '2025-06-22 14:10:55.522155', '30', 'rondelle plate', 1, '[{`added`: {}}]', 13, 1),
(58, '2025-06-22 14:11:12.579504', '29', 'Ecrou', 2, '[{`changed`: {`fields`: [`Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(59, '2025-06-22 14:21:09.290463', '29', 'Ecrou', 2, '[{`changed`: {`fields`: [`Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(60, '2025-06-22 14:22:54.133046', '2', 'fil attache', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(61, '2025-06-22 14:37:49.482915', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(62, '2025-06-22 14:37:59.868878', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[]', 13, 1),
(63, '2025-06-22 14:38:11.743416', '26', 'Ancrage en forme de crochet', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(64, '2025-06-22 14:45:16.396393', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(65, '2025-06-22 14:45:43.617470', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(66, '2025-06-22 14:46:28.493049', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(67, '2025-06-22 14:46:50.862849', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(68, '2025-06-22 14:47:21.077219', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[]', 13, 1),
(69, '2025-06-22 14:47:32.612229', '26', 'Ancrage en forme de crochet', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(70, '2025-06-22 14:47:41.782949', '25', 'Ancrage en forme de crosse', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(71, '2025-06-22 14:47:55.017917', '24', 'Ancrage simple', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(72, '2025-06-22 14:48:06.558252', '23', 'Ancrage forme L', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(73, '2025-06-22 14:48:19.062911', '22', 'Ancrage forme J', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(74, '2025-06-22 14:50:22.360282', '21', 'etrier a fond triangulaire', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(75, '2025-06-22 14:51:13.673096', '21', 'etrier a fond triangulaire', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(76, '2025-06-22 14:52:45.743446', '21', 'etrier a fond triangulaire', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(77, '2025-06-22 14:53:04.617985', '20', 'etrier a une seul branche a fond droit', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(78, '2025-06-22 14:53:14.806055', '19', 'etrier a fond droit', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(79, '2025-06-22 14:53:23.553315', '18', 'etrier a une seul branche a fond circulaire', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(80, '2025-06-22 14:56:38.251680', '17', 'etrier a fond circulaire', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(81, '2025-06-22 15:07:01.615367', '27', 'Ancrage en forme de crochet à double cambrure', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(82, '2025-06-22 15:07:54.715800', '21', 'etrier a fond triangulaire', 2, '[]', 13, 1),
(83, '2025-06-22 15:14:17.379512', '16', 'barre coude aux deux extremites', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(84, '2025-06-22 15:14:36.064922', '15', 'barre coude a une extremite', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(85, '2025-06-22 15:15:57.650331', '15', 'barre coude a une extremite', 2, '[]', 13, 1),
(86, '2025-06-22 15:16:07.565411', '14', 'barre droite', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Description`]}}]', 13, 1),
(87, '2025-06-22 15:17:24.958839', '14', 'barre droite', 2, '[{`changed`: {`fields`: [`Sous categorie`]}}]', 13, 1),
(88, '2025-06-22 15:27:16.589403', '5', 'cadre triangulaire', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Description`]}}]', 13, 1),
(89, '2025-06-22 15:27:39.471901', '4', 'cadre hexagonale', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Description`]}}]', 13, 1),
(90, '2025-06-22 15:28:02.674010', '3', 'cadre rectangle', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Description`]}}]', 13, 1),
(91, '2025-06-22 15:28:30.887403', '1', 'cadre carre', 2, '[{`changed`: {`fields`: [`Sous categorie`, `Description`]}}]', 13, 1),
(92, '2025-06-22 15:36:07.366599', '29', 'Ecrou hexagonale', 2, '[{`changed`: {`fields`: [`Nom`, `Description`]}}]', 13, 1),
(93, '2025-06-22 15:36:17.339154', '30', 'rondelle plate', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(94, '2025-06-22 15:36:35.089788', '30', 'rondelle plate', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(95, '2025-06-22 15:38:39.673151', '28', 'fer a beton de 12m', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(96, '2025-06-22 15:41:12.929444', '28', 'fer a beton de 12m', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(97, '2025-06-22 15:46:30.933448', '2', 'fil d\'attache', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 13, 1),
(98, '2025-06-22 15:47:02.922120', '29', 'Ecrou hexagonale', 2, '[]', 13, 1),
(99, '2025-06-22 15:48:14.312787', '2', 'fil d\'attache', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(100, '2025-06-22 15:49:35.415029', '16', 'barre coude aux deux extremites', 2, '[]', 13, 1),
(101, '2025-06-22 15:49:48.593285', '13', 'cintrage du crochet', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(102, '2025-06-22 15:50:10.723300', '12', 'cintrage de la pince', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(103, '2025-06-22 15:50:21.211518', '11', 'cintrage en T economique', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(104, '2025-06-22 15:51:32.364179', '10', 'cintrage en U ferme', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(105, '2025-06-22 15:51:42.674244', '9', 'cintrage en U ouvert', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(106, '2025-06-22 15:51:52.529432', '8', 'cintrage en U', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(107, '2025-06-22 15:52:05.779379', '7', 'cintrage en T', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(108, '2025-06-22 15:52:17.272054', '6', 'cintrage de l\'etrier', 2, '[{`changed`: {`fields`: [`Description`]}}]', 13, 1),
(109, '2025-06-28 11:27:17.985151', '1', 'FerPrice object (1)', 1, '[{`added`: {}}]', 19, 1),
(110, '2025-06-28 11:29:22.457845', '2', 'FerPrice object (2)', 1, '[{`added`: {}}]', 19, 1),
(111, '2025-06-28 11:29:50.863720', '3', 'FerPrice object (3)', 1, '[{`added`: {}}]', 19, 1),
(112, '2025-06-28 11:30:49.648828', '4', 'FerPrice object (4)', 1, '[{`added`: {}}]', 19, 1),
(113, '2025-06-28 11:31:03.601341', '5', 'FerPrice object (5)', 1, '[{`added`: {}}]', 19, 1),
(114, '2025-06-28 11:31:20.865031', '6', 'FerPrice object (6)', 1, '[{`added`: {}}]', 19, 1),
(115, '2025-06-28 11:31:37.490535', '7', 'FerPrice object (7)', 1, '[{`added`: {}}]', 19, 1),
(116, '2025-06-28 11:31:48.165574', '8', 'FerPrice object (8)', 1, '[{`added`: {}}]', 19, 1),
(117, '2025-06-28 11:32:01.208846', '9', 'FerPrice object (9)', 1, '[{`added`: {}}]', 19, 1),
(118, '2025-06-28 11:32:23.369936', '10', 'FerPrice object (10)', 1, '[{`added`: {}}]', 19, 1),
(119, '2025-06-28 11:33:20.618632', '11', 'FerPrice object (11)', 1, '[{`added`: {}}]', 19, 1),
(120, '2025-06-28 11:34:08.308999', '12', 'FerPrice object (12)', 1, '[{`added`: {}}]', 19, 1),
(121, '2025-06-28 11:37:27.943394', '13', 'FerPrice object (13)', 1, '[{`added`: {}}]', 19, 1),
(122, '2025-06-28 12:54:21.241115', '1', 'm6', 2, '[]', 19, 1),
(123, '2025-07-01 17:58:20.349020', '1', 'm6', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(124, '2025-07-01 17:58:30.023954', '2', 'm8', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(125, '2025-07-01 17:58:41.148957', '3', 'm10', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(126, '2025-07-01 17:59:02.094074', '13', 'm12', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(127, '2025-07-01 17:59:22.334226', '4', 'm14', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(128, '2025-07-01 17:59:49.289418', '5', 'm16', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(129, '2025-07-01 18:00:11.429096', '6', 'm20', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(130, '2025-07-01 18:00:26.004366', '7', 'm24', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(131, '2025-07-01 18:00:42.279147', '8', 'm27', 2, '[]', 19, 1),
(132, '2025-07-01 18:00:59.949517', '8', 'm27', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(133, '2025-07-01 18:01:08.669201', '9', 'm30', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(134, '2025-07-01 18:01:14.019167', '9', 'm30', 2, '[]', 19, 1),
(135, '2025-07-01 18:01:25.669412', '10', 'm32', 2, '[{`changed`: {`fields`: [`Prix`]}}]', 19, 1),
(136, '2025-07-08 16:29:44.928252', '29', 'Ecrou hexagonale', 2, '[{`changed`: {`fields`: [`Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(137, '2025-07-12 13:26:06.765284', '29', 'Ecrou hexagonale', 2, '[{`changed`: {`fields`: [`Imageshop3d`, `Imageshop2d`]}}]', 13, 1),
(138, '2025-07-15 18:16:02.643408', '1', 'Partenariats object (1)', 1, '[{`added`: {}}]', 20, 1),
(139, '2025-07-15 20:30:42.134636', '1', 'nao cooporation', 2, '[{`changed`: {`fields`: [`Date fin`]}}]', 20, 1),
(140, '2025-07-15 20:39:06.488707', '1', 'nao cooporation', 2, '[{`changed`: {`fields`: [`Date fin`]}}]', 20, 1),
(141, '2025-07-16 07:10:36.050577', '1', 'Projet object (1)', 1, '[{`added`: {}}]', 21, 1),
(142, '2025-07-16 07:10:47.855334', '1', 'Projet object (1)', 3, '', 21, 1),
(143, '2025-07-16 07:12:05.396062', '4', 'Eagan Nicholson', 1, '[{`added`: {}}]', 20, 1),
(144, '2025-07-16 07:12:48.705177', '2', 'Projet object (2)', 1, '[{`added`: {}}]', 21, 1),
(145, '2025-07-19 20:37:14.062605', '2', 'Sage Gay', 2, '[{`changed`: {`fields`: [`User`]}}]', 20, 1),
(146, '2025-07-28 16:26:28.011652', '1', 'nao cooporation', 2, '[{`changed`: {`fields`: [`Date fin`]}}]', 20, 1),
(147, '2025-08-12 12:54:33.136227', '3', 'NANA NANGMO, ROMEO - 1645.00', 3, '', 16, 1),
(148, '2025-08-12 12:54:42.354598', '4', 'NANA NANGMO, ROMEO - 7596.00', 3, '', 16, 1),
(149, '2025-08-12 12:54:49.115674', '5', 'NANA NANGMO, ROMEO - 98139.00', 3, '', 16, 1),
(150, '2025-08-12 12:54:54.320727', '6', 'NANA NANGMO, ROMEO - 3338558.00', 3, '', 16, 1),
(151, '2025-08-12 12:55:00.287766', '7', 'NANA NANGMO, ROMEO - 2276958.00', 3, '', 16, 1),
(152, '2025-08-12 12:55:05.911349', '8', 'NANA NANGMO, ROMEO - 981876.00', 3, '', 16, 1),
(153, '2025-08-12 13:12:50.950994', '2', 'OrderUserInfo object (2)', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 28, 1),
(154, '2025-08-12 13:13:06.977555', '2', 'OrderUserInfo object (2)', 2, '[{`changed`: {`fields`: [`Nom`]}}]', 28, 1),
(155, '2025-08-13 16:11:58.489077', '2', 'citoyen du buzz', 2, '[{`changed`: {`fields`: [`Adresse`]}}]', 28, 1),
(156, '2025-08-17 14:50:52.123630', '1', 'nao cooporation', 3, '', 20, 1),
(157, '2025-08-18 14:28:30.983064', '1', 'CodePromo object (1)', 1, '[{`added`: {}}]', 30, 1),
(158, '2025-08-18 14:31:41.226627', '2', 'CodePromo object (2)', 1, '[{`added`: {}}]', 30, 1),
(159, '2025-08-18 17:23:03.675272', '1', 'Article 2', 1, '[{`added`: {}}]', 31, 1),
(160, '2025-08-19 02:02:39.206917', '13', 'Adipisicing ut id id incididunt aut anim quae exercitation obcaecati necessitatibus', 3, '', 31, 1),
(161, '2025-08-19 02:02:47.798662', '12', 'Nihil omnis quia sunt et non dolore obcaecati qui id quae sunt in eveniet autem', 3, '', 31, 1),
(162, '2025-08-19 02:02:52.789719', '11', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(163, '2025-08-19 02:03:01.316297', '10', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(164, '2025-08-19 02:03:06.413219', '9', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(165, '2025-08-19 02:03:11.217658', '8', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(166, '2025-08-19 02:03:15.775740', '7', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(167, '2025-08-19 02:03:22.396499', '6', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(168, '2025-08-19 02:03:32.280322', '3', 'Saepe minima debitis', 3, '', 31, 1),
(169, '2025-08-19 02:03:38.585456', '5', 'Nisi ea sint dolores sequi voluptatem vitae inventore molestiae assumenda vitae aut officiis aliquip', 3, '', 31, 1),
(170, '2025-08-19 02:03:43.453352', '4', 'Blanditiis qui', 3, '', 31, 1),
(171, '2025-08-19 02:03:50.621752', '2', 'image 66', 3, '', 31, 1),
(172, '2025-08-19 02:03:55.010827', '1', 'Article 2', 3, '', 31, 1),
(173, '2025-08-19 11:57:15.951787', '16', 'Repellendus Quia officiis voluptas et', 3, '', 31, 1),
(174, '2025-08-21 11:12:10.640610', '3', 'Howard, Tyler', 3, '', 7, 1),
(175, '2025-08-21 11:34:29.542500', '4', 'Britt, Daryl', 3, '', 7, 1),
(176, '2025-08-21 11:37:57.845852', '5', 'Downs, Aretha', 3, '', 7, 1);

-- --------------------------------------------------------

--
-- Structure de la table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=30 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `django_content_type`
--

INSERT IGNORE INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'permission'),
(3, 'auth', 'group'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session'),
(6, 'auth_app', 'customuser'),
(7, 'produits', 'categorie'),
(8, 'produits', 'produit'),
(9, 'produits', 'ferprice'),
(10, 'usesOrders', 'cart'),
(11, 'usesOrders', 'cartitem'),
(12, 'usesOrders', 'order'),
(13, 'usesOrders', 'orderitem'),
(14, 'usesOrders', 'traiment'),
(15, 'usesOrders', 'orderuserinfo'),
(16, 'usesOrders', 'payment'),
(17, 'usesOrders', 'codepromo'),
(18, 'fer', 'fer'),
(19, 'fer', 'mouvement'),
(20, 'contact', 'contact'),
(21, 'contact', 'contactfile'),
(22, 'partenaires', 'partenariats'),
(23, 'partenaires', 'projet'),
(24, 'partenaires', 'projetitem'),
(25, 'partenaires', 'projetorder'),
(26, 'partenaires', 'paiementprojet'),
(27, 'partenaires', 'projetorderitem'),
(28, 'partenaires', 'traimentorder'),
(29, 'archives', 'archives');

-- --------------------------------------------------------

--
-- Structure de la table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=68 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `django_migrations`
--

INSERT IGNORE INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-08-30 12:52:58.238309'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-08-30 12:52:58.433853'),
(3, 'auth', '0001_initial', '2025-08-30 12:52:59.449183'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-08-30 12:52:59.565926'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-08-30 12:52:59.570926'),
(6, 'auth', '0004_alter_user_username_opts', '2025-08-30 12:52:59.580925'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-08-30 12:52:59.585929'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-08-30 12:52:59.590922'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-08-30 12:52:59.595933'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-08-30 12:52:59.605931'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-08-30 12:52:59.615947'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-08-30 12:52:59.718222'),
(13, 'auth', '0011_update_proxy_permissions', '2025-08-30 12:52:59.728227'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-08-30 12:52:59.739870'),
(15, 'auth_app', '0001_initial', '2025-08-30 12:53:00.943796'),
(16, 'admin', '0001_initial', '2025-08-30 12:53:01.296059'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-08-30 12:53:01.306065'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-08-30 12:53:01.316082'),
(19, 'archives', '0001_initial', '2025-08-30 12:53:01.542806'),
(20, 'archives', '0002_alter_archives_file', '2025-08-30 12:53:01.557579'),
(21, 'auth_app', '0002_customuser_is_partenaire', '2025-08-30 12:53:01.723309'),
(22, 'auth_app', '0003_customuser_email_verified', '2025-08-30 12:53:01.882626'),
(23, 'contact', '0001_initial', '2025-08-30 12:53:02.157338'),
(24, 'contact', '0002_contact_file_alter_contact_type', '2025-08-30 12:53:02.241635'),
(25, 'contact', '0003_alter_contact_file', '2025-08-30 12:53:02.246657'),
(26, 'contact', '0004_contact_file_response', '2025-08-30 12:53:02.334821'),
(27, 'contact', '0005_alter_contact_type', '2025-08-30 12:53:02.339817'),
(28, 'fer', '0001_initial', '2025-08-30 12:53:02.608048'),
(29, 'fer', '0002_remove_fer_type_fer_alter_fer_categorie', '2025-08-30 12:53:02.772837'),
(30, 'fer', '0003_fer_unique_diametre_categorie', '2025-08-30 12:53:02.913217'),
(31, 'fer', '0004_mouvement_prix_u', '2025-08-30 12:53:03.006792'),
(32, 'fer', '0005_fer_user_mouvement_user_and_more', '2025-08-30 12:53:03.535342'),
(33, 'fer', '0006_fer_longueur_critique', '2025-08-30 12:53:03.788702'),
(34, 'produits', '0001_initial', '2025-08-30 12:53:04.214698'),
(35, 'produits', '0002_alter_produit_sous_categorie', '2025-08-30 12:53:04.305217'),
(36, 'produits', '0003_ferprice_alter_produit_sous_categorie', '2025-08-30 12:53:04.352268'),
(37, 'produits', '0004_alter_ferprice_diametre_alter_ferprice_prix', '2025-08-30 12:53:04.432854'),
(38, 'produits', '0005_ferprice_prixrevient', '2025-08-30 12:53:04.516528'),
(39, 'partenaires', '0001_initial', '2025-08-30 12:53:04.747731'),
(40, 'partenaires', '0002_alter_partenariats_email_alter_partenariats_name', '2025-08-30 12:53:04.912704'),
(41, 'partenaires', '0003_alter_partenariats_name_projet_projetitem_and_more', '2025-08-30 12:53:05.857811'),
(42, 'partenaires', '0004_paimenentprojet_alter_projet_created_at_and_more', '2025-08-30 12:53:05.936309'),
(43, 'partenaires', '0005_delete_paimenentprojet_projet_reduction', '2025-08-30 12:53:06.076779'),
(44, 'partenaires', '0006_projetorder', '2025-08-30 12:53:06.414365'),
(45, 'partenaires', '0007_alter_projetitem_projet', '2025-08-30 12:53:06.434361'),
(46, 'partenaires', '0008_alter_projetorder_projet_item', '2025-08-30 12:53:06.449361'),
(47, 'partenaires', '0009_alter_projetorder_projet_item', '2025-08-30 12:53:06.474390'),
(48, 'partenaires', '0010_paiementprojet', '2025-08-30 12:53:06.849460'),
(49, 'partenaires', '0011_remove_projetorder_projet_item_and_more', '2025-08-30 12:53:08.211048'),
(50, 'partenaires', '0012_traimentorder', '2025-08-30 12:53:08.562549'),
(51, 'partenaires', '0013_projetitem_prix_revient', '2025-08-30 12:53:08.792120'),
(52, 'sessions', '0001_initial', '2025-08-30 12:53:08.887277'),
(53, 'usesOrders', '0001_initial', '2025-08-30 12:53:09.512404'),
(54, 'usesOrders', '0002_order_orderitem', '2025-08-30 12:53:10.031098'),
(55, 'usesOrders', '0003_rename_userr_order_user', '2025-08-30 12:53:10.698022'),
(56, 'usesOrders', '0004_remove_order_statut_traiment', '2025-08-30 12:53:11.149530'),
(57, 'usesOrders', '0005_traiment_created_at', '2025-08-30 12:53:11.283933'),
(58, 'usesOrders', '0006_orderuserinfo', '2025-08-30 12:53:11.570201'),
(59, 'usesOrders', '0007_payment', '2025-08-30 12:53:11.695549'),
(60, 'usesOrders', '0008_codepromo', '2025-08-30 12:53:12.013861'),
(61, 'usesOrders', '0009_alter_codepromo_expiration', '2025-08-30 12:53:12.177848'),
(62, 'usesOrders', '0010_codepromo_created_at', '2025-08-30 12:53:12.292619'),
(63, 'usesOrders', '0011_cart_remise_order_remise', '2025-08-30 12:53:12.536006'),
(64, 'usesOrders', '0012_orderuserinfo_mode_livraison', '2025-08-30 12:53:12.675470'),
(65, 'usesOrders', '0013_cartitem_prix_revient_orderitem_prix_revient', '2025-08-30 12:53:12.922753'),
(66, 'usesOrders', '0014_alter_cartitem_cart', '2025-08-30 12:53:12.953602'),
(67, 'usesOrders', '0015_alter_cart_remise', '2025-08-30 12:53:12.973603');

-- --------------------------------------------------------

--
-- Structure de la table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `fer_fer`
--

DROP TABLE IF EXISTS `fer_fer`;
CREATE TABLE IF NOT EXISTS `fer_fer` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `diametre` varchar(255) NOT NULL,
  `categorie` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `longueur_critique` int(10) UNSIGNED DEFAULT NULL CHECK (`longueur_critique` >= 0),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_diametre_categorie` (`diametre`,`categorie`),
  KEY `fer_fer_user_id_90cf871f` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `fer_fer`
--

INSERT IGNORE INTO `fer_fer` (`id`, `diametre`, `categorie`, `created_at`, `user_id`, `longueur_critique`) VALUES
(1, '6', 'barre', '2025-06-12 11:56:20.030971', NULL, 500),
(2, '10', 'barre', '2025-06-12 12:18:55.702538', NULL, 500),
(3, '6', 'rouleau', '2025-06-12 12:22:39.549360', NULL, 500),
(4, '20', 'rouleau', '2025-06-13 06:54:37.987459', NULL, 500),
(5, '16', 'barre', '2025-06-13 06:58:08.750461', 1, 500),
(6, '30', 'barre', '2025-06-13 14:23:02.691775', 1, 600);

-- --------------------------------------------------------

--
-- Structure de la table `fer_mouvement`
--

DROP TABLE IF EXISTS `fer_mouvement`;
CREATE TABLE IF NOT EXISTS `fer_mouvement` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` datetime(6) NOT NULL,
  `quantite` int(10) UNSIGNED DEFAULT NULL CHECK (`quantite` >= 0),
  `longueur_m` decimal(10,2) DEFAULT NULL,
  `type_mouvement` varchar(10) NOT NULL,
  `fer_id` bigint(20) NOT NULL,
  `prix_u` int(10) UNSIGNED DEFAULT NULL CHECK (`prix_u` >= 0),
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fer_mouvement_fer_id_4ae55478` (`fer_id`),
  KEY `fer_mouvement_user_id_bd82f0f9` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `fer_mouvement`
--

INSERT IGNORE INTO `fer_mouvement` (`id`, `date`, `quantite`, `longueur_m`, `type_mouvement`, `fer_id`, `prix_u`, `user_id`) VALUES
(1, '2025-06-12 20:39:52.340552', 30, '12.00', '', 1, 4600, NULL),
(2, '2025-06-12 20:40:35.963352', 73, '45.00', '', 2, 24, NULL),
(3, '2025-06-12 20:41:09.375881', 73, '45.00', '', 2, 24, NULL),
(4, '2025-06-12 20:41:18.591845', 24, '19.00', '', 1, 59, NULL),
(5, '2025-06-12 21:00:39.700877', 96, '100.00', 'entree', 1, 72, NULL),
(6, '2025-06-13 06:58:26.139473', 28, '29.00', 'entree', 1, 85, 1),
(7, '2025-06-13 19:30:50.202838', 82, '32.00', 'entree', 5, 54, 1),
(8, '2025-06-13 19:30:50.362833', 82, '32.00', 'entree', 5, 54, 1);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_paiementprojet`
--

DROP TABLE IF EXISTS `partenaires_paiementprojet`;
CREATE TABLE IF NOT EXISTS `partenaires_paiementprojet` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tranche` smallint(5) UNSIGNED NOT NULL CHECK (`tranche` >= 0),
  `date_paiement` datetime(6) NOT NULL,
  `mode_paiement` varchar(100) DEFAULT NULL,
  `projet_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `partenaires_paiementprojet_projet_id_tranche_9e32aedf_uniq` (`projet_id`,`tranche`),
  KEY `partenaires_paiementprojet_projet_id_8d65a90d` (`projet_id`),
  KEY `partenaires_paiementprojet_user_id_86dbf56d` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_paiementprojet`
--

INSERT IGNORE INTO `partenaires_paiementprojet` (`id`, `tranche`, `date_paiement`, `mode_paiement`, `projet_id`, `user_id`) VALUES
(1, 1, '2025-07-29 15:14:23.301977', 'virement bancaire', 4, 1),
(2, 2, '2025-07-29 15:44:42.018824', 'virement bancaire', 4, 1),
(3, 3, '2025-07-29 15:45:28.543135', 'virement bancaire', 4, 1),
(4, 1, '2025-07-29 16:03:52.924567', 'virement bancaire', 3, 1),
(5, 2, '2025-07-29 18:19:24.968060', 'virement bancaire', 3, 1),
(6, 3, '2025-08-03 16:38:34.147229', 'virement bancaire', 3, 1);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_partenariats`
--

DROP TABLE IF EXISTS `partenaires_partenariats`;
CREATE TABLE IF NOT EXISTS `partenaires_partenariats` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(254) NOT NULL,
  `adresse` varchar(255) NOT NULL,
  `telephone` varchar(200) NOT NULL,
  `date_debut` datetime(6) NOT NULL,
  `date_fin` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `partenaires_partenariats_email_0845fa6d_uniq` (`email`),
  UNIQUE KEY `partenaires_partenariats_name_fc002c28_uniq` (`name`),
  KEY `partenaires_partenariats_user_id_4448c9e7` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_partenariats`
--

INSERT IGNORE INTO `partenaires_partenariats` (`id`, `name`, `email`, `adresse`, `telephone`, `date_debut`, `date_fin`, `user_id`) VALUES
(2, 'Sage Gay', 'jyvo@mailinator.com', 'Voluptas a ipsum qui animi elit tempora sequi', '+1 (906) 389-7766', '1977-03-19 00:00:00.000000', '2030-01-22 00:00:00.000000', 1),
(3, 'Indigo Davidson', 'ruzofo@mailinator.com', 'Proident a qui voluptate nisi obcaecati eos neque nulla expedita reprehenderit in aut anim molestiae dolores delectus tenetur in', '+1 (678) 681-7696', '2017-11-05 00:00:00.000000', '1985-11-06 00:00:00.000000', 2),
(4, 'Eagan Nicholson', 'zojy@mailinator.com', 'Tempora in qui et eaque cupidatat cupidatat omnis et deserunt reprehenderit beatae incididunt optio eum quas eligendi', '+1 (447) 629-4596', '2025-07-16 07:11:54.000000', '2025-07-16 07:12:03.000000', 1);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_projet`
--

DROP TABLE IF EXISTS `partenaires_projet`;
CREATE TABLE IF NOT EXISTS `partenaires_projet` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `statut` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `partenariat_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `reduction` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `unique_name_partenariat` (`name`,`partenariat_id`),
  KEY `partenaires_projet_partenariat_id_4dff9a8e` (`partenariat_id`),
  KEY `partenaires_projet_user_id_b1a436fe` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_projet`
--

INSERT IGNORE INTO `partenaires_projet` (`id`, `name`, `statut`, `created_at`, `update_at`, `partenariat_id`, `user_id`, `reduction`) VALUES
(2, 'Beau Carey', 'en cours', '2025-07-16 07:12:48.689805', '2025-07-16 07:12:48.689805', 2, 1, 15),
(3, 'Shaine Briggs', 'en cours', '2025-07-20 11:56:48.996201', '2025-07-20 11:56:48.996201', 4, 1, 47),
(4, 'projet3', 'en cours', '2025-07-27 11:34:21.219742', '2025-07-27 11:34:21.220309', 2, 1, 4),
(5, 'DALAGE', 'en cours', '2025-08-24 13:53:51.002226', '2025-08-24 13:53:51.002226', 2, 1, 5);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_projetitem`
--

DROP TABLE IF EXISTS `partenaires_projetitem`;
CREATE TABLE IF NOT EXISTS `partenaires_projetitem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `quantite` int(10) UNSIGNED NOT NULL CHECK (`quantite` >= 0),
  `prix_u` decimal(10,2) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  `projet_id` bigint(20) NOT NULL,
  `prix_revient` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partenaires_projetitem_produit_id_3398bf42` (`produit_id`),
  KEY `partenaires_projetitem_projet_id_be7dfeff` (`projet_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_projetitem`
--

INSERT IGNORE INTO `partenaires_projetitem` (`id`, `details`, `quantite`, `prix_u`, `produit_id`, `projet_id`, `prix_revient`) VALUES
(1, '{\"prix_Total\": 240.0, \"longueur_Barre\": 12.0, \"Diametre_fer\": \"6\", \"type_de_fer\": \"Fe400\"}', 3, '80.00', 28, 3, '909.00'),
(2, '{\"fer\": \"bending iron\", \"diametre_fer\": \"6\", \"rayon_Courbure\": 10.0, \"longueur_Depart_et_Fin\": 30.0}', 2101, '124.00', 7, 3, '3.00');

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_projetorder`
--

DROP TABLE IF EXISTS `partenaires_projetorder`;
CREATE TABLE IF NOT EXISTS `partenaires_projetorder` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `projet_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partenaires_projetorder_projet_id_2d3527fc` (`projet_id`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_projetorder`
--

INSERT IGNORE INTO `partenaires_projetorder` (`id`, `created_at`, `projet_id`) VALUES
(14, '2025-08-03 16:31:18.660237', 4),
(15, '2025-08-03 16:34:49.611707', 3),
(16, '2025-08-17 15:33:00.737378', 4);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_projetorderitem`
--

DROP TABLE IF EXISTS `partenaires_projetorderitem`;
CREATE TABLE IF NOT EXISTS `partenaires_projetorderitem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quantite` int(10) UNSIGNED NOT NULL CHECK (`quantite` >= 0),
  `projet_item_id` bigint(20) NOT NULL,
  `projet_order_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partenaires_projetorderitem_projet_item_id_63d613fc` (`projet_item_id`),
  KEY `partenaires_projetorderitem_projet_order_id_86e50e92` (`projet_order_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_projetorderitem`
--

INSERT IGNORE INTO `partenaires_projetorderitem` (`id`, `quantite`, `projet_item_id`, `projet_order_id`) VALUES
(1, 1, 3, 14),
(2, 1, 4, 14),
(3, 1, 5, 14),
(4, 3, 1, 15),
(5, 2101, 2, 15),
(6, 1, 3, 15),
(7, 4, 3, 16),
(8, 13, 4, 16),
(9, 12, 5, 16);

-- --------------------------------------------------------

--
-- Structure de la table `partenaires_traimentorder`
--

DROP TABLE IF EXISTS `partenaires_traimentorder`;
CREATE TABLE IF NOT EXISTS `partenaires_traimentorder` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `statut` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `projet_order_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `partenaires_traimentorder_projet_order_id_58165b8a` (`projet_order_id`),
  KEY `partenaires_traimentorder_user_id_34aab5a4` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `partenaires_traimentorder`
--

INSERT IGNORE INTO `partenaires_traimentorder` (`id`, `statut`, `created_at`, `projet_order_id`, `user_id`) VALUES
(1, 'en_attente', '2025-08-03 16:31:19.374543', 14, 1),
(2, 'en_attente', '2025-08-03 16:34:50.221894', 15, 1),
(3, 'en_production', '2025-08-06 12:14:46.830130', 14, 1),
(4, 'pret_pour_livraison', '2025-08-06 12:14:58.810910', 14, 1),
(5, 'en_attente', '2025-08-17 15:33:01.323990', 16, 1),
(6, 'en_production', '2025-08-18 14:08:42.955034', 16, 1),
(7, 'pret_pour_livraison', '2025-08-18 14:08:48.347249', 16, 1),
(8, 'termine', '2025-08-18 14:17:54.616133', 16, 1),
(9, 'termine', '2025-08-19 13:16:37.963084', 14, 1),
(10, 'termine', '2025-08-19 13:16:57.421565', 14, 1),
(11, 'en_production', '2025-08-19 13:28:28.630472', 15, 1);

-- --------------------------------------------------------

--
-- Structure de la table `produits_categorie`
--

DROP TABLE IF EXISTS `produits_categorie`;
CREATE TABLE IF NOT EXISTS `produits_categorie` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `libelle` varchar(255) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `produits_categorie`
--

INSERT IGNORE INTO `produits_categorie` (`id`, `libelle`, `image`) VALUES
(1, 'CINTRAGE DU FER A BETON', 'produits/images/CINTRAGE_DU_FER_A_BETON.jpg'),
(2, 'CINTRAGE DU FER ROND', 'produits/images/CINTRAGE_DU_FER_ROND.jpg'),
(3, 'QUICAILLERIE', 'produits/images/QUICAILLERIE.jpg');

-- --------------------------------------------------------

--
-- Structure de la table `produits_ferprice`
--

DROP TABLE IF EXISTS `produits_ferprice`;
CREATE TABLE IF NOT EXISTS `produits_ferprice` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `diametre` varchar(255) NOT NULL,
  `prix` double NOT NULL,
  `prixRevient` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `diametre` (`diametre`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `produits_ferprice`
--

INSERT IGNORE INTO `produits_ferprice` (`id`, `diametre`, `prix`, `prixRevient`) VALUES
(1, 'm6', 1650, NULL),
(2, 'm8', 3000, NULL),
(3, 'm10', 4650, NULL),
(4, 'm14', 9700, NULL),
(5, 'm16', 10200, NULL),
(6, 'm20', 11000, NULL),
(7, 'm24', 11800, NULL),
(8, 'm27', 12560, NULL),
(9, 'm30', 13500, NULL),
(10, 'm32', 14100, NULL),
(11, 'taux', 0.04, NULL),
(12, 'taxe', 4, NULL),
(13, 'm12', 6650, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `produits_produit`
--

DROP TABLE IF EXISTS `produits_produit`;
CREATE TABLE IF NOT EXISTS `produits_produit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) NOT NULL,
  `sous_categorie` varchar(255) DEFAULT NULL,
  `imageshop3d` varchar(100) NOT NULL,
  `imageshop2d` varchar(100) NOT NULL,
  `image_sous_categorie` varchar(100) DEFAULT NULL,
  `name_page` varchar(255) NOT NULL,
  `Description` longtext DEFAULT NULL,
  `categorie_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_sous_categorie_nom` (`sous_categorie`,`nom`),
  KEY `produits_produit_categorie_id_857419d4` (`categorie_id`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `produits_produit`
--

INSERT IGNORE INTO `produits_produit` (`id`, `nom`, `sous_categorie`, `imageshop3d`, `imageshop2d`, `image_sous_categorie`, `name_page`, `Description`, `categorie_id`) VALUES
(1, 'cadre carre', 'Cintrage de cadre', 'produits/images/CADRE_CARRE.jpg', 'produits/images/IMG-0_03.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_7L6v0oU.jpg', 'cadre-carre', 'Disponible sous plusieurs tailles et diamètres M6/M8/M10/M12 mm', 1),
(2, 'fil d\'attache', 'Quincaillerie', 'produits/images/fil_dattache.jpg', 'produits/images/fil_dattache_fN4Mt0k.jpg', '', 'barre-droite', 'Disponible en anneau de 1kg', 3),
(3, 'cadre rectangle', 'Cintrage de cadre', 'produits/images/CADRE_RECTANGULAIRE.jpg', 'produits/images/IMG-0_04.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_6ZeXMZ4.jpg', 'cadre-rectangle', 'Disponible sous plusieurs tailles et diamètres M6/M8/M10/M12 mm', 1),
(4, 'cadre hexagonale', 'Cintrage de cadre', 'produits/images/CADRE_HEXAGONALE.jpg', 'produits/images/IMG-0_05.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_0B8ZMsi.jpg', 'cadre-hexagonale', 'Disponible sous plusieurs tailles et diamètres M6/M8/M10/M12 mm', 1),
(5, 'cadre triangulaire', 'Cintrage de cadre', 'produits/images/CADRE_TRIANGULAIRE.jpg', 'produits/images/IMG-0_06.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_nbRbGmr.jpg', 'cadre-triangulaire', 'Disponible sous plusieurs tailles et diamètres M6/M8/M10/M12 mm', 1),
(6, 'cintrage de l\'etrier', 'Cintrage de forme', 'produits/images/CADRE_EN_ETRIER_cTudCSi.jpg', 'produits/images/IMG-0_07_mDPFPD0.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_XC26D54.jpg', 'cintrage-etrier', 'Disponible sous plusieurs tailles et diamètres', 1),
(7, 'cintrage en T', 'Cintrage de forme', 'produits/images/CADRE_EN_T_MYZWykF.jpg', 'produits/images/IMG-0_08_tcVfTfG.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_Jo6O13w.jpg', 'cintrage-T', 'Disponible sous plusieurs tailles et diamètres', 1),
(8, 'cintrage en U', 'Cintrage de forme', 'produits/images/CADRE_EN_U_R9DmZPp.jpg', 'produits/images/IMG-0_09_IEyVlIL.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_QX556lY.jpg', 'cintrage-U', 'Disponible sous plusieurs tailles et diamètres', 1),
(9, 'cintrage en U ouvert', 'Cintrage de forme', 'produits/images/CADRE_EN_U_OUVERT_RqRb2GT.jpg', 'produits/images/IMG-0_10_0atV0W6.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_woKIbYd.jpg', 'cintrage-U-ouvert', 'Disponible sous plusieurs tailles et diamètres', 1),
(10, 'cintrage en U ferme', 'Cintrage de forme', 'produits/images/CADRE_EN_U_FERME_jLI9w7d.jpg', 'produits/images/IMG-0_11_1NIYzdO.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_6hG5HfX.jpg', 'cintrage-U-ferne', 'Disponible sous plusieurs tailles et diamètres', 1),
(11, 'cintrage en T economique', 'Cintrage de forme', 'produits/images/CADRE_EN_T_3m_RjOw3Cj.jpg', 'produits/images/IMG-0_12_v4s1rSY.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_OtXcG2o.jpg', 'cintrage-T-economique', 'Disponible sous plusieurs tailles et diamètres', 1),
(12, 'cintrage de la pince', 'Cintrage de forme', 'produits/images/FORME_EN_PINCE_8OYRb8f.jpg', 'produits/images/IMG-0_13_IFtGP2v.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_CvTDlr2.jpg', 'cintrage-pince', 'Disponible sous plusieurs tailles et diamètres', 1),
(13, 'cintrage du crochet', 'Cintrage de forme', 'produits/images/FORME_Z_pFwHmta.jpg', 'produits/images/IMG-0_14_TuDc5ut.jpg', 'produits/images/CINTRAGE_DE_CADRE_ET_FORMES_tuxyhfs.jpg', 'cintrage-crochet', 'Disponible sous plusieurs tailles et diamètres', 1),
(14, 'barre droite', 'redressage et decoupage', 'produits/images/ARMATURE_BARRE_DROITE_9iZFd1x.jpg', 'produits/images/IMG-0.jpg', 'produits/images/REDRESSAGE_ET_DECOUPAGE.jpg', 'barre-droite', 'Disponible sous plusieurs tailles et diamètres', 1),
(15, 'barre coude a une extremite', 'cintrage d\'extremite', 'produits/images/ARMATURE_COUDEE_A_LEXTREMITEE_HDaR9KH.jpg', 'produits/images/IMG-0_01.jpg', 'produits/images/CINTRAGE_DEXTREMITEE.jpg', 'barre-coude-a-une-extremite', 'Disponible sous plusieurs tailles et diamètres', 1),
(16, 'barre coude aux deux extremites', 'cintrage d\'extremite', 'produits/images/ARMATURE_COUDEE_AUX_LEXTREMITEES_FZ8GAtd.jpg', 'produits/images/IMG-0_02_OEm1saP.jpg', 'produits/images/CINTRAGE_DEXTREMITEE_hxo4Zkn.jpg', 'barre-coude-aux-deux-extremite', 'Disponible sous plusieurs tailles et diamètres', 1),
(17, 'etrier a fond circulaire', 'Etrier pour bardage et toiture', 'produits/images/Etrier_a_fond_circulaire.jpg', 'produits/images/IMG-0_17.jpg', 'produits/images/ETRIER_POUR_TOITURE_ET_BARDAGE.jpg', 'etrier-fond-circulaire', 'Disponible en acier lisse  de M6/\r\n\r\nM8/M10/M12/M14/M16/M20 mm', 2),
(18, 'etrier a une seul branche a fond circulaire', 'Etrier pour bardage et toiture', 'produits/images/Etrier_a_une_seul_branche_a_fond_circulaire.jpg', 'produits/images/IMG-0_18_nnqGJPx.jpg', 'produits/images/ETRIER_POUR_TOITURE_ET_BARDAGE_vcvuyrR.jpg', 'etrier-une-branche-fond-circulaire', 'Disponible en acier lisse  de M6/\r\n\r\nM8/M10/M12/M14/M16/M20 mm', 2),
(19, 'etrier a fond droit', 'Etrier pour bardage et toiture', 'produits/images/Etrier_a_fond_droit.jpg', 'produits/images/IMG-0_15_gtTrBmH.jpg', 'produits/images/ETRIER_POUR_TOITURE_ET_BARDAGE_gRbgvMh.jpg', 'etrier-fond-droit', 'Disponible en acier lisse  de M6/\r\n\r\nM8/M10/M12/M14/M16/M20 mm', 2),
(20, 'etrier a une seul branche a fond droit', 'Etrier pour bardage et toiture', 'produits/images/Etrier_a_une_seul_branche_a_fond_droit.jpg', 'produits/images/IMG-0_16_dMVzl4E.jpg', 'produits/images/ETRIER_POUR_TOITURE_ET_BARDAGE_sqtyjoh.jpg', 'etrier-une-branche-fond-droit', 'Disponible en acier lisse  de M6/\r\n\r\nM8/M10/M12/M14/M16/M20 mm', 2),
(21, 'etrier a fond triangulaire', 'Etrier pour bardage et toiture', 'produits/images/Etrier_a_fond_triangulaire.jpg', 'produits/images/IMG-0_19_LU4sHQe.jpg', 'produits/images/ETRIER_POUR_TOITURE_ET_BARDAGE_6UJaHrU.jpg', 'etrier-fond-triangulaire', 'Disponible en acier lisse  de M6/\r\n\r\nM8/M10/M12/M14/M16/M20 mm', 2),
(22, 'Ancrage forme J', 'boulon d\'ancrage a beton', 'produits/images/ancrage_en_forme_de_J.jpg', 'produits/images/IMG-0_21_cAGyo4e.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON.jpg', 'ancrage-forme-J', 'Disponible en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(23, 'Ancrage forme L', 'boulon d\'ancrage a beton', 'produits/images/ancrage_en_forme_de_L.jpg', 'produits/images/IMG-0_20_RAzxKYs.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON_JsSumAr.jpg', 'ancrage-forme-L', 'Disponible en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(24, 'Ancrage simple', 'boulon d\'ancrage a beton', 'produits/images/ancrage_simple.jpg', 'produits/images/IMG-0_25.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON_HCm0tYo.jpg', 'ancrage-simple', 'Disponible en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(25, 'Ancrage en forme de crosse', 'boulon d\'ancrage a beton', 'produits/images/ancrage_en_forme_de_crosse.jpg', 'produits/images/IMG-0_22_j6DkqM5.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON_chRuwop.jpg', 'ancrage-forme-crosse', 'Disponible en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(26, 'Ancrage en forme de crochet', 'boulon d\'ancrage a beton', 'produits/images/ancrage_en_forme_de_crochet.jpg', 'produits/images/IMG-0_23_8z089Xl.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON_OldUv9E.jpg', 'ancrage-forme-crochet', 'Disponible en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(27, 'Ancrage en forme de crochet à double cambrure', 'boulon d\'ancrage a beton', 'produits/images/ancrage_en_forme_de_crochet_a_double_cambrure.jpg', 'produits/images/IMG-0_24_d6xp3vA.jpg', 'produits/images/BOULONS_DANCRAGE_A_BETON_nM5EiF1.jpg', 'ancrage-crochet-double-cambrure', 'Disponible sous plusieurs tailles en acier lisse ou crénelé de M12/M16/M20/M24/M27/M30/\r\n\r\nM32 mm', 2),
(28, 'fer a beton de 12m', 'Quincaillerie', 'produits/images/fer_quincaillerie.jpg', 'produits/images/fer_quincaillerie_PcSNbZR.jpg', '', 'quincaillerie', 'Disponible sous plusieurs diamètres M6/M8/M10/M12/M14/M16/M20\r\n\r\n/M25/M32 mm', 3),
(29, 'Ecrou hexagonale', 'Quincaillerie', 'produits/images/1000117798_1.jpg', 'produits/images/1000117798_1_mGJtktm.jpg', '', 'ecrou', 'Disponible sous plusieurs tailles et diamètres', 3),
(30, 'rondelle plate', 'Quincaillerie', 'produits/images/rondelle.jpg', 'produits/images/rondelle_XcrGoWN.jpg', '', 'rondelle', 'Disponible sous plusieurs tailles et diamètres', 3);

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_cart`
--

DROP TABLE IF EXISTS `usesorders_cart`;
CREATE TABLE IF NOT EXISTS `usesorders_cart` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `remise` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_cart_user_id_5c19f53a` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=55 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `usesorders_cart`
--

INSERT IGNORE INTO `usesorders_cart` (`id`, `created_at`, `updated_at`, `user_id`, `remise`) VALUES
(24, '2025-08-21 12:26:49.381941', '2025-08-21 12:26:49.381941', 6, '1.00'),
(54, '2025-08-27 16:55:21.981084', '2025-08-27 16:55:21.982083', 1, '0.00');

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_cartitem`
--

DROP TABLE IF EXISTS `usesorders_cartitem`;
CREATE TABLE IF NOT EXISTS `usesorders_cartitem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `quantite` int(10) UNSIGNED NOT NULL CHECK (`quantite` >= 0),
  `prix_u` decimal(10,2) NOT NULL,
  `cart_id` bigint(20) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  `prix_revient` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_cartitem_cart_id_8a233100` (`cart_id`),
  KEY `usesOrders_cartitem_produit_id_7edbb7af` (`produit_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `usesorders_cartitem`
--

INSERT IGNORE INTO `usesorders_cartitem` (`id`, `details`, `quantite`, `prix_u`, `cart_id`, `produit_id`, `prix_revient`) VALUES
(1, '{\"fer\": \"bending iron\", \"Diametre_fer\": \"12\", \"Angle_pliage\": 120, \"rayon_Courbure\": 60.0, \"longueur_Depart_et_Fin\": 60.0, \"diametre\": 966.0, \"longueur_Total\": 3333.24, \"prix_Total\": 13649.0}', 7, '1950.00', 24, 4, '2.00'),
(2, '{\"fer\": \"bending iron\", \"Diametre_fer\": \"8\", \"Angle_pliage\": 135, \"rayon_Courbure\": 40.0, \"longueur_Depart_et_Fin\": 40.0, \"longueur_Cote\": 445.0, \"longueur_Total\": 1499.0}', 9, '426.00', 54, 5, '288.00'),
(3, '{\"fer\": \"bending iron\", \"Diametre_fer\": \"36\", \"longeur_Filetage\": 108.0, \"longeur_Ancrage\": 200, \"diametre_Cintrage\": 72.0, \"hauteur_Cintrage\": 108.0, \"longueur_Total\": 380.0}', 30, '1165.00', 54, 27, '33000.00');

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_codepromo`
--

DROP TABLE IF EXISTS `usesorders_codepromo`;
CREATE TABLE IF NOT EXISTS `usesorders_codepromo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `remise` decimal(10,2) NOT NULL,
  `code` varchar(255) NOT NULL,
  `expiration` int(10) UNSIGNED NOT NULL,
  `client_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_codepromo_client_id_9da528de` (`client_id`),
  KEY `usesOrders_codepromo_user_id_166354e8` (`user_id`)
) ;

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_order`
--

DROP TABLE IF EXISTS `usesorders_order`;
CREATE TABLE IF NOT EXISTS `usesorders_order` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `remise` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_order_userr_id_c1279ef7` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_orderitem`
--

DROP TABLE IF EXISTS `usesorders_orderitem`;
CREATE TABLE IF NOT EXISTS `usesorders_orderitem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `quantite` int(10) UNSIGNED NOT NULL CHECK (`quantite` >= 0),
  `prix_u` decimal(10,2) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  `prix_revient` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_orderitem_order_id_3e874792` (`order_id`),
  KEY `usesOrders_orderitem_produit_id_416e250d` (`produit_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_orderuserinfo`
--

DROP TABLE IF EXISTS `usesorders_orderuserinfo`;
CREATE TABLE IF NOT EXISTS `usesorders_orderuserinfo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) NOT NULL,
  `telephone` varchar(255) NOT NULL,
  `adresse` varchar(255) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `mode_livraison` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_orderuserinfo_order_id_7304c0fc` (`order_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `usesorders_orderuserinfo`
--

INSERT IGNORE INTO `usesorders_orderuserinfo` (`id`, `nom`, `telephone`, `adresse`, `order_id`, `mode_livraison`) VALUES
(1, 'Alice Zenker', '655927237', 'Ange raphael campus 2', 9, 'livraison sur chantier'),
(2, 'citoyen du buzz', '+1 (834) 258-5789', 'lendi derriere la chefferie', 10, 'livraison sur chantier'),
(3, 'Veritatis ea quasi ad cumque nulla quam Nam ullamco', '+1 (482) 153-3358', 'kotto', 11, 'livraison sur chantier');

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_payment`
--

DROP TABLE IF EXISTS `usesorders_payment`;
CREATE TABLE IF NOT EXISTS `usesorders_payment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `amount_paid` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `usesorders_traiment`
--

DROP TABLE IF EXISTS `usesorders_traiment`;
CREATE TABLE IF NOT EXISTS `usesorders_traiment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `statut` varchar(20) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usesOrders_traiment_order_id_b2c71afb` (`order_id`),
  KEY `usesOrders_traiment_user_id_0010a914` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `usesorders_traiment`
--

INSERT IGNORE INTO `usesorders_traiment` (`id`, `statut`, `order_id`, `user_id`, `created_at`) VALUES
(14, 'en_attente', 9, 1, '2025-08-12 12:41:39.221422'),
(15, 'en_attente', 10, 1, '2025-08-12 12:42:49.913785'),
(16, 'en_attente', 11, 1, '2025-08-17 15:30:07.216447'),
(17, 'en_production', 9, 1, '2025-08-19 13:11:28.774259');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
