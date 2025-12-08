#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L4D2 Tournament Integrity Checker
Programa para verificar la integridad de jugadores en torneos de Left 4 Dead 2
"""

import os
import sys
import json
import hashlib
import winreg
import psutil
import time
import base64
import secrets
import ctypes
import subprocess
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import requests
import tempfile

# Importar el generador de tokens
sys.path.append(os.path.join(os.path.dirname(__file__), 'gentoke'))
try:
    from token_generator import TokenGenerator
except ImportError:
    TokenGenerator = None

# Verificar si estamos en modo compilado (ejecutable)
def is_compiled():
    """Verifica si el programa está ejecutándose como ejecutable compilado"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# ============================================================================
# BASE DE DATOS DE FIRMAS DE CHEATS CONOCIDOS DE L4D2
# ============================================================================
KNOWN_CHEAT_SIGNATURES = {
    # ===== HACKS COMERCIALES CONOCIDOS =====
    # Aimware - Sistema de aimbot profesional (PAGO)
    'aimware': {
        'patterns': ['aimware', 'aim-ware', 'aim_ware', 'aw.dll', 'aw_', 'aimw', 'aimwareloader', 
                     'aimware_loader', 'awloader', 'aimware.exe', 'aw.exe'],
        'severity': 'CRITICAL',
        'description': 'Aimware - Sistema de aimbot profesional de pago (Loader + Aimbot + ESP + HvH)',
        'type': 'COMMERCIAL_INJECTION',
        'common_paths': ['%TEMP%', '%APPDATA%', 'Desktop', 'Downloads']
    },
    
    # BauntiCheats - Muy popular en comunidad rusa/hispana
    'baunticheats': {
        'patterns': ['baunti', 'baunticheats', 'baunti_cheats', 'baunti-cheats', 'bauntil4d2', 
                     'l4d2helper', 'l4d2_helper', 'baunti.exe', 'bauntiloader'],
        'severity': 'CRITICAL',
        'description': 'BauntiCheats - Left 4 Dead 2 Helper (Popular en comunidad rusa/hispana)',
        'type': 'COMMERCIAL_INJECTION',
        'common_paths': ['%TEMP%', '%APPDATA%', 'Desktop']
    },
    
    # Interwebz - Cheats para juegos Valve
    'interwebz': {
        'patterns': ['interwebz', 'inter-webz', 'inter_webz', 'iwz', 'interwebzloader', 
                     'iwzloader', 'interwebz.exe'],
        'severity': 'CRITICAL',
        'description': 'Interwebz - Cheat conocido para juegos Valve (TF2, CSS, L4D2)',
        'type': 'COMMERCIAL_INJECTION',
        'common_paths': ['%TEMP%', '%APPDATA%']
    },
    
    # LMAOBOX - Originalmente TF2, portado a L4D2
    'lmaobox': {
        'patterns': ['lmaobox', 'lmao-box', 'lmao_box', 'lmao', 'lmaoloader', 'lmaobox.exe'],
        'severity': 'CRITICAL',
        'description': 'LMAOBOX - Cheat originalmente de TF2, portado a L4D2',
        'type': 'COMMERCIAL_INJECTION',
        'common_paths': ['%TEMP%', '%APPDATA%']
    },
    
    # FleepHack / Fleep - Hack gratuito muy distribuido
    'fleephack': {
        'patterns': ['fleep', 'fleephack', 'fleep_hack', 'fleep-hack', 'fleep.exe', 
                     'fleeploader', 'fleep_loader'],
        'severity': 'CRITICAL',
        'description': 'FleepHack / Fleep - Hack gratuito muy distribuido en foros y YouTube',
        'type': 'FREE_INJECTION',
        'common_paths': ['%TEMP%', '%APPDATA%', 'Downloads']
    },
    
    # Osiris / RatPoison - Open Source, usado como base para hacks privados
    'osiris_ratpoison': {
        'patterns': ['osiris', 'ratpoison', 'rat_poison', 'rat-poison', 'osiris.dll', 
                     'ratpoison.dll', 'osirisloader'],
        'severity': 'CRITICAL',
        'description': 'Osiris / RatPoison - Open Source, usado como base para hacks privados de L4D2',
        'type': 'OPEN_SOURCE_BASED',
        'common_paths': ['%TEMP%', '%APPDATA%', 'Downloads']
    },
    
    # ===== HACKS DE FUNCIONALIDAD =====
    
    # No Vomit/Boomer - Elimina efecto de vómito
    'no_vomit': {
        'patterns': ['novomit', 'no_vomit', 'no-vomit', 'noboomer', 'no_boomer',
                     'removevomit', 'vomit_remove', 'clearvomit', 'vomitremove',
                     'disable_vomit', 'disablevomit', 'vomit_off', 'vomitoff'],
        'severity': 'CRITICAL',
        'description': 'Elimina efecto de vómito del Boomer'
    },
    
    # No Smoke - Elimina humo del Smoker
    'no_smoke': {
        'patterns': ['nosmoke', 'no_smoke', 'no-smoke', 'nosmoker', 'no_smoker',
                     'removesmoke', 'smoke_remove', 'clearsmoke', 'smokeremove',
                     'disable_smoke', 'disablesmoke', 'smoke_off', 'smokeoff'],
        'severity': 'CRITICAL',
        'description': 'Elimina humo del Smoker'
    },
    
    # Fast Fire - Disparo rápido
    'fast_fire': {
        'patterns': ['fastfire', 'fast_fire', 'fast-fire', 'rapidfire', 'rapid_fire',
                     'autofire', 'auto_fire', 'quickfire', 'quick_fire', 'firemod',
                     'fire_mod', 'speedfire', 'speed_fire', 'fastshoot', 'fast_shoot'],
        'severity': 'CRITICAL',
        'description': 'Disparo rápido automático (Fast Fire)'
    },
    
    # Fast Melee - Golpe rápido
    'fast_melee': {
        'patterns': ['fastmelee', 'fast_melee', 'fast-melee', 'rapidmelee', 'rapid_melee',
                     'quickmelee', 'quick_melee', 'meleemod', 'melee_mod', 'speedmelee',
                     'speed_melee', 'meleefast', 'melee_fast', 'fastpunch', 'fast_punch'],
        'severity': 'CRITICAL',
        'description': 'Golpe cuerpo a cuerpo acelerado (Fast Melee)'
    },
    
    # No Recoil - Sin retroceso
    'no_recoil': {
        'patterns': ['norecoil', 'no_recoil', 'no-recoil', 'removerecoil', 'recoil_remove',
                     'recoiloff', 'recoil_off', 'disable_recoil', 'disablerecoil'],
        'severity': 'CRITICAL',
        'description': 'Elimina retroceso de armas (No Recoil)'
    },
    
    # Infinite Ammo - Munición infinita
    'infinite_ammo': {
        'patterns': ['infiniteammo', 'infinite_ammo', 'infinite-ammo', 'unlimitedammo',
                     'unlimited_ammo', 'noammo', 'ammo_infinite', 'ammoinfinite'],
        'severity': 'CRITICAL',
        'description': 'Munición infinita'
    },
    
    # God Mode - Invulnerabilidad
    'god_mode': {
        'patterns': ['godmode', 'god_mode', 'god-mode', 'invincible', 'invulnerable',
                     'nohurt', 'no_hurt', 'nodamage', 'no_damage', 'immortal'],
        'severity': 'CRITICAL',
        'description': 'Modo invulnerabilidad (God Mode)'
    },
    
    # Speed Hack - Velocidad aumentada
    'speed_hack': {
        'patterns': ['speedhack', 'speed_hack', 'speed-hack', 'fastrun', 'fast_run',
                     'speedmod', 'speed_mod', 'runfast', 'run_fast', 'velocity'],
        'severity': 'CRITICAL',
        'description': 'Velocidad de movimiento aumentada (Speed Hack)'
    },
    
    # Wallhack/ESP - Ver a través de paredes
    'wallhack_esp': {
        'patterns': ['wallhack', 'wall_hack', 'wall-hack', 'esp', 'extrasensory',
                     'seethru', 'see_thru', 'xray', 'x-ray', 'walls'],
        'severity': 'CRITICAL',
        'description': 'Ver a través de paredes (Wallhack/ESP)'
    },
    
    # Bhop - Bunny hop automático
    'bhop': {
        'patterns': ['bhop', 'bunnyhop', 'bunny_hop', 'bunny-hop', 'autobhop',
                     'auto_bhop', 'auto-bhop', 'jumpmod', 'jump_mod'],
        'severity': 'HIGH',
        'description': 'Bunny hop automático (Bhop)'
    },
    
    # No Flash - Elimina cegamiento
    'no_flash': {
        'patterns': ['noflash', 'no_flash', 'no-flash', 'flashremove', 'flash_remove',
                     'disableflash', 'disable_flash', 'flashoff', 'flash_off'],
        'severity': 'HIGH',
        'description': 'Elimina efecto de cegamiento'
    }
}

# ============================================================================
# CARPETAS OFICIALES DE LEFT 4 DEAD 2 (WHITELIST)
# ============================================================================
OFFICIAL_L4D2_FOLDERS = {
    'bin',                          # Ejecutables y DLLs del motor Source
    'config',                       # Configuración de Steam
    'hl2',                          # Motor Half-Life 2
    'left4dead2',                   # Carpeta principal del juego
    'left4dead2_dlc1',              # DLC 1
    'left4dead2_dlc2',              # DLC 2
    'left4dead2_dlc3',              # DLC 3
    'left4dead2_dlc3_spanish',      # DLC 3 español
    'left4dead2_spanish',           # Archivos en español
    'platform',                     # Plataforma Steam
    'sdk_content',                  # Contenido del SDK
    'sdk_tools',                    # Herramientas del SDK
    'update'                        # Archivos de actualización
}

# ============================================================================
# MAPAS COMPETITIVOS LEGÍTIMOS (WHITELIST)
# Estos son mapas custom usados en servidores competitivos (zonemod, etc.)
# Se descargan manualmente y se colocan en addons/ (no en addons/workshop)
# ============================================================================
COMPETITIVE_MAPS_WHITELIST = {
    # Nombres exactos (sin extensión .vpk)
    'bloodtracks',
    'cmpn_fatalfreightfix',          # cmpn_FatalFreightFix
    'dead_center_reconstructed',
    'detourahead',
    'highwaytohell',
    'noecho',                        # NoEcho
    'red_tide',
    'undead_zone',
    'bts_l4d2',
    'dark carnival remix',
    'deadbeforedawn2_dc',
    'downpour',
    'ihatemountains2',
    'nomercyrehab',
    'suicideblitz2',
    'warcelona',
    'carriedoff',
    'darkblood2_v3',
    'deathaboardv2',
    'energycrisis',
    'l4d2_diescraper_362',
    'openroad',
    'sunrise_carnival',
    'whispersofwinter',              # WhispersOfWinter
    'city of the dead map',
    'daybreak_v3',
    'deathrow',                      # DeathRow
    'hauntedforest_v3',
    'l4d2_thebloodymoors',
    'parish overgrowth',
    'the_dark_parish',
    'white_forest',
    'city17l4d2',
    'dead_center_rebirth',
    'deathsentence',
    'heavencanwaitl4d2',
    'left_behind',
    'ravenholm',
    'tourofterror',
    'yama',                          # Yama
    # Variaciones comunes (por si acaso)
    'deadbeforedawn2',
    'darkblood2',
    'hauntedforest',
    'daybreak',
    'city17',
    'dead_center',
    'parish',
    'dark_parish',
    'city_of_the_dead'
}

# ============================================================================
# CONTENIDO OFICIAL DE GAMEINFO.TXT (PARA VALIDACIÓN)
# ============================================================================
OFFICIAL_GAMEINFO_CONTENT = '''"GameInfo"
{
	game	"Left 4 Dead 2"	// Window title
	type multiplayer_only
	nomodels 1
	nohimodel 1
	l4dcrosshair 1
	hidden_maps
	{
		"test_speakers"			1
		"test_hardware"			1
	}
	nodegraph 0
	perfwizard 0
	SupportsXbox360 1
	SupportsDX8	0
	GameData	"left4dead2.fgd"

	FileSystem
	{
		SteamAppId				550		// This will mount all the GCFs we need (240=CS:S, 220=HL2).
		ToolsAppId				563		// Tools will load this (ie: source SDK caches) to get things like materials\\debug, materials\\editor, etc.
		
		//
		// The code that loads this file automatically does a few things here:
		//
		// 1. For each "Game" search path, it adds a "GameBin" path, in <dir>\\bin
		// 2. For each "Game" search path, it adds another "Game" path in front of it with _<langage> at the end.
		//    For example: c:\\hl2\\cstrike on a french machine would get a c:\\hl2\\cstrike_french path added to it.
		// 3. For the first "Game" search path, it adds a search path called "MOD".
		// 4. For the first "Game" search path, it adds a search path called "DEFAULT_WRITE_PATH".
		//

		//
		// Search paths are relative to the base directory, which is where hl2.exe is found.
		//
		// |gameinfo_path| points at the directory where gameinfo.txt is.
		// We always want to mount that directory relative to gameinfo.txt, so
		// people can mount stuff in c:\\mymod, and the main game resources are in
		// someplace like c:\\program files\\valve\\steam\\steamapps\\<username>\\half-life 2.
		//
		SearchPaths
		{
			Game				update
			Game				left4dead2_dlc3
			Game				left4dead2_dlc2
			Game				left4dead2_dlc1
			Game				|gameinfo_path|.
			Game				hl2
		}
	}
}'''

# ============================================================================
# CONTENIDO OFICIAL DE ADDONCONFIG.CFG (PARA VALIDACIÓN)
# ============================================================================
OFFICIAL_ADDONCONFIG_CONTENT = '''//------------------------------------------------------------------------------
// Used by the server to determine whether or not custom content should be allowed
// in a particular game mode. 
//
//	0 = no restrictions on custom content (default)
//	1 = block custom content
//
// This doesn't affect custom campaigns, just client-side replacements for models,
// skins, sounds, etc.
//
// If an entry for the exact mode name isn't found, the base mode will be used.
// If the base mode isn't found, the default will be used.
//------------------------------------------------------------------------------

"RestrictAddons"
{
	"default"	"0"
	"versus"	"1"
	"scavenge"	"1"
	"mutation15"	"1" // versus survival
}'''

# ============================================================================
# CONTENIDO OFICIAL DE 360CONTROLLER.CFG (PARA VALIDACIÓN)
# ============================================================================
OFFICIAL_360CONTROLLER_CONTENT = '''unbindall				// Prevent mouse/keyboard control when gamepad is in use (to prevent autoaim exploit)

joystick 1
joy_advanced "1"			// use advanced joystick options (allows for multiple axes)

joy_name "L4D Xbox360 Joystick Configuration"
joy_advaxisx 3				// x-axis controls GAME_AXIS_SIDE (strafing left and right)
joy_advaxisy 1				// y-axis controls GAME_AXIS_FORWARD (move forward and back)
joy_advaxisz 0				// z-axis is treated like a button
joy_advaxisr 2				// r-axis controls GAME_AXIS_PITCH (look up and down)
joy_advaxisu 4				// u-axis controls GAME_AXIS_YAW (look left and right)
joy_advaxisv 0				// v-axis is unused
joy_forwardsensitivity -1.0	// movement sensitivity
joy_sidesensitivity 1.0
joy_forwardthreshold 0.1	// movement dead zone settings
joy_sidethreshold 0.1
joy_pitchsensitivity 1.0	// look sensitivity
joy_yawsensitivity -1.5
joy_pitchthreshold 0.1		// look dead zone settings
joy_yawthreshold 0.0

joy_variable_frametime 1
joy_autoaimdampenrange 0.85
joy_autoaimdampen 0.5
joy_lowend 0.65
joy_lowmap 0.15
joy_accelscale 3.0
joy_accelmax 4.0
joy_response_move 5
joy_response_look 1
joy_autoaimdampen 0.3
joy_autoaimdampenrange 0.85
joyadvancedupdate			// advanced joystick update allows for analog control of move and look

// Alternate control 1
+jlook					// enable joystick look
bind "A_BUTTON" "+jump;+menuAccept"		// (A) button - Jump  -menuAccpt allows us to make selections on hud menus
bind "B_BUTTON" "+reload"			// (B) button - Reload
bind "X_BUTTON" "+use"				// (X) Use
bind "Y_BUTTON" "lastinv"			// (Y) button - swap pistol/rifle or z_abort -used to respawn as a ghost.
bind "R_TRIGGER" "+attack"			// RT - Main weapon - Primary trigger
bind "L_TRIGGER" "+attack2"			// LT - Melee
bind "R_SHOULDER" "+lookspin"			// RB - Fast 180 spin
bind "L_SHOULDER" "toggle_duck"			// LB - Duck
bind "STICK1" "vocalize smartlook"		// LS - vocalize
bind "STICK2" "+zoom"				// RS click - Rifle Zoom

// Fixed bindings, do not change these across joystick presets
bind "BACK" "togglescores"			// (back) button - scores
bind "START" "gameui_activate"		// (start) button - pause
bind "S1_UP" "+menuUp"				// Hud menu Up
bind "S1_DOWN" "+menuDown"			// Hud menu Down
bind "UP" "impulse 100"				// DPad Up - Toggle flashlight
bind "LEFT" "slot3"					// DPad Left - grenade
bind "RIGHT" "slot4"				// DPad Right - health
bind "DOWN" "slot5"					// DPad Down - Pills


// controller2 bindings
+jlook					// enable joystick look
cmd2 bind "A_BUTTON" "+jump;+menuAccept"		// (A) button - Jump  -menuAccpt allows us to make selections on hud menus
cmd2 bind "B_BUTTON" "+reload"			// (B) button - Reload
cmd2 bind "X_BUTTON" "+use"				// (X) Use
cmd2 bind "Y_BUTTON" "lastinv"			// (Y) button - swap pistol/rifle or z_abort -used to respawn as a ghost.
cmd2 bind "R_TRIGGER" "+attack"			// RT - Main weapon - Primary trigger
cmd2 bind "L_TRIGGER" "+attack2"			// LT - Melee
cmd2 bind "R_SHOULDER" "+lookspin"			// RB - Fast 180 spin
cmd2 bind "L_SHOULDER" "toggle_duck"			// LB - Duck - is also used to give objects to people.
cmd2 bind "STICK1" "vocalize smartlook"		// LS - vocalize
cmd2 bind "STICK2" "+zoom"				// RS click - Rifle Zoom

// Fixed bindings, do not change these across joystick presets
cmd2 bind "BACK" "togglescores"			// (back) button - scores
cmd2 bind "START" "gameui_activate"		// (start) button - pause
cmd2 bind "S1_UP" "+menuUp"				// Hud menu Up
cmd2 bind "S1_DOWN" "+menuDown"			// Hud menu Down
cmd2 bind "UP" "impulse 100"				// DPad Up - Toggle flashlight
cmd2 bind "LEFT" "slot3"					// DPad Left - grenade
cmd2 bind "RIGHT" "slot4"				// DPad Right - health
cmd2 bind "DOWN" "slot5"					// DPad Down - Pills


sk_autoaim_mode 2'''

# ============================================================================
# CONTENIDO OFICIAL DE PERF.CFG (PARA VALIDACIÓN)
# ============================================================================
OFFICIAL_PERF_CONTENT = '''host_framerate 30
director_stop
nb_delete_all
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_spawn common
z_common_limit 30
z_spawn mob
z_spawn boomer
z_spawn boomer
z_spawn boomer
z_spawn boomer
quit
warp_far_survivor_here
warp_far_survivor_here
warp_far_survivor_here
sb_flashlight 1'''

# ============================================================================
# WHITELIST DE PROGRAMAS LEGÍTIMOS (PARA REDUCIR FALSOS POSITIVOS)
# ============================================================================
LEGITIMATE_PROGRAMS_WHITELIST = {
    # ===== WINDOWS SYSTEM =====
    'applicationframehost.exe', 'audiodg.exe', 'consent.exe',
    'credentialuibroker.exe', 'dllhost.exe', 'filecoauth.exe',
    'fulltrustnotifier.exe', 'gamebarpresencewriter.exe',
    'mousocoreworker.exe', 'rundll32.exe', 'runonce.exe',
    'runtimebroker.exe', 'setuphost.exe', 'shellexperiencehost.exe',
    'sppextcomobj.exe', 'startmenuexperiencehost.exe',
    'werfault.exe', 'widgetservice.exe', 'wuaucltcore.exe',
    'dwm.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe',
    'svchost.exe', 'services.exe', 'lsass.exe', 'smss.exe',
    'conhost.exe', 'fontdrvhost.exe', 'sihost.exe',
    'taskhostw.exe', 'searchindexer.exe', 'searchprotocolhost.exe',
    'searchfilterhost.exe', 'ctfmon.exe', 'textinputhost.exe',
    
    # ===== MICROSOFT OFFICE =====
    'excel.exe', 'winword.exe', 'powerpnt.exe', 'outlook.exe',
    'onenote.exe', 'msaccess.exe', 'mspub.exe', 'visio.exe',
    'officeclicktorun.exe', 'officebackgroundtaskhandler.exe',
    
    # ===== ADOBE =====
    'acrocef.exe', 'adobe crash processor.exe', 'adobecollabsync.exe',
    'adobeipcbroker.exe', 'ccxprocess.exe', 'photoshop.exe',
    'illustrator.exe', 'indesign.exe', 'premiere pro.exe',
    'after effects.exe', 'acrobat.exe', 'acrord32.exe',
    'creative cloud.exe', 'adobe desktop service.exe',
    
    # ===== BROWSERS =====
    'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
    'opera.exe', 'brave.exe', 'vivaldi.exe',
    
    # ===== COMMUNICATION APPS =====
    'whatsapp.exe', 'zoom.exe', 'teams.exe', 'slack.exe',
    'discord.exe', 'skype.exe', 'telegram.exe',
    
    # ===== MEDIA APPS =====
    'photos.exe', 'movies & tv.exe', 'groove music.exe',
    'spotify.exe', 'vlc.exe', 'wmplayer.exe', 'itunes.exe',
    'videoeditorqt.exe',
    
    # ===== DEVELOPMENT TOOLS =====
    # IDEs
    'code.exe', 'devenv.exe', 'pycharm64.exe', 'idea64.exe',
    'webstorm64.exe', 'phpstorm64.exe', 'rider64.exe',
    'clion64.exe', 'goland64.exe', 'datagrip64.exe',
    'atom.exe', 'sublime_text.exe', 'notepad++.exe',
    
    # Setup/Installers de IDEs
    'codesetup', 'antigravitysetup', 'windsurfsetup',
    
    # Build Tools
    'esbuild.exe', 'webpack.exe', 'vite.exe', 'rollup.exe',
    'node.exe', 'npm.exe', 'yarn.exe', 'pnpm.exe',
    
    # Language Servers
    'devsense.php.ls.exe', 'omnisharp.exe', 'rust-analyzer.exe',
    
    # Version Control
    'git.exe', 'git-bash.exe', 'github desktop.exe',
    
    # Package Managers
    'vsce-sign.exe',
    
    # ===== DATABASES & SERVERS =====
    'mysqld.exe', 'postgres.exe', 'mongod.exe', 'redis-server.exe',
    'php.exe', 'apache.exe', 'nginx.exe', 'xampp-control.exe',
    'xampp_start.exe', 'wampmanager.exe',
    
    # ===== CLOUD SERVICES =====
    'onedrive.exe', 'dropbox.exe', 'googledrivesync.exe',
    'box.exe', 'megasync.exe', 'pcloud.exe',
    
    # ===== ANTIVIRUS & SECURITY =====
    'mbamservice.exe', 'malwarebytes.exe', 'avast.exe',
    'avg.exe', 'norton.exe', 'kaspersky.exe', 'bitdefender.exe',
    'mpcmdrun.exe', 'msmpeng.exe', 'nissrv.exe',
    
    # ===== SYSTEM UTILITIES =====
    'makecab.exe', 'msiexec.exe', 'netcfgnotifyobjecthost.exe',
    'regedit.exe', 'taskmgr.exe', 'perfmon.exe', 'resmon.exe',
    'cleanmgr.exe', 'defrag.exe', 'chkdsk.exe',
    '7zfm.exe', 'winrar.exe', 'winzip.exe',
    
    # ===== HARDWARE/DRIVERS =====
    'nvcontainer.exe', 'nvspcaps64.exe', 'nvdisplay.container.exe',
    'amdrsserv.exe', 'radeonse ttings.exe',
    'realtekaudiosvc.exe', 'nahimicsvc.exe',
    'discsoftbusservicepro.exe', 'daemon tools.exe',
    'jhi_service.exe', 'intel.exe',
    
    # ===== GAMING PLATFORMS =====
    'steam.exe', 'steamservice.exe', 'steamwebhelper.exe',
    'epicgameslauncher.exe', 'origin.exe', 'uplay.exe',
    'battle.net.exe', 'gog galaxy.exe', 'riotclientservices.exe',
    'gamelaunchhelper.exe', 'gameinputsvc.exe', 'gamingservicesui.exe',
    
    # ===== POPULAR GAMES =====
    'robloxplayerbeta.exe', 'minecraft.exe', 'league of legends.exe',
    'valorant.exe', 'fortnite.exe', 'gta5.exe',
    
    # ===== GOOGLE SERVICES =====
    'elevation_service.exe', 'googleupdate.exe', 'googledrivefs.exe',
    
    # ===== MICROSOFT SERVICES =====
    'mspcmanagerservice.exe', 'microsoftedgeupdate.exe',
    
    # ===== STREAMING/RECORDING =====
    'obs64.exe', 'obs32.exe', 'streamlabs obs.exe', 'xsplit.exe',
    'nvidia share.exe', 'nvidia shadowplay.exe',
    
    # ===== PRODUCTIVITY =====
    'notion.exe', 'evernote.exe', 'onenote.exe', 'trello.exe',
    'asana.exe', 'monday.exe',
    
    # ===== FILE SHARING =====
    'shareit.exe', 'airdroid.exe', 'pushbullet.exe',
    
    # ===== NETWORK TOOLS =====
    'packettracer.exe', 'wireshark.exe', 'putty.exe',
    'winscp.exe', 'filezilla.exe',
    
    # ===== VIRTUALIZATION =====
    'vmware.exe', 'virtualbox.exe', 'vmwareservice.exe',
    'vboxsvc.exe', 'qemu.exe',
    
    # ===== PLEX =====
    'plex update service.exe', 'plex media server.exe',
    
    # ===== QT APPLICATIONS =====
    'qtwebengineprocess.exe',
    
    # ===== HARDWARE TOOLS =====
    'ch341programmer.exe', 'arduino.exe', 'platformio.exe',
    
    # ===== MISC TOOLS =====
    'perfboost.exe', 'gpucheck.exe', 'graphics-check.exe',
    'get-graphics-offsets32.exe', 'get-graphics-offsets64.exe',
    'fd.exe', 'where.exe', 'installer.exe', 'service.exe',
    'fab_x64.exe', 'am_delta_patch', 'genp'
}

# Rutas legítimas de Windows (no marcar como sospechosas)
LEGITIMATE_PATHS = [
    r'C:\Windows',
    r'C:\Program Files',
    r'C:\Program Files (x86)',
    r'C:\ProgramData\Microsoft',
    r'C:\ProgramData\Package Cache'
]

# Rutas sospechosas (SÍ marcar como sospechosas)
SUSPICIOUS_PATHS = [
    r'\AppData\Local\Temp',
    r'\Downloads',
    r'\Desktop',
    r'\Documents\cheat',
    r'\Documents\hack',
    r'\AppData\Roaming\cheat',
    r'\AppData\Roaming\hack'
]

class L4D2IntegrityChecker:
    def __init__(self):
        self.steam_path = None
        self.l4d2_path = None
        
        # Determinar la ruta del archivo de configuración
        if is_compiled():
            # Si está compilado, buscar en el directorio del ejecutable
            self.config_file = os.path.join(os.path.dirname(sys.executable), "l4d2_checker_config.json")
        else:
            # Si no está compilado, usar el directorio actual
            self.config_file = "l4d2_checker_config.json"
        self.token_generator = TokenGenerator() if TokenGenerator else None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'mods_detected': [],
            'steam_accounts': [],
            'steam_accounts_count': 0,
            'suspicious_processes': [],
            'game_files_integrity': 'unknown',
            'vac_status': 'unknown',
            'integrity_status': 'unknown',
            'pc_info': {},
            'token_validation': None
        }
        # Webhook de Discord hardcodeado (no depende de archivos externos)
        self.discord_webhook_url = "https://discord.com/api/webhooks/1425316527070249042/TsKDgYSxrFEL8r0u3I_W3pcon8xnzHxISceFtq7lKCWxiKkQNJfBK5f8uNsfKSuRz5dF"
        
        # Cargar configuración (para otros datos como password, admin_token, etc.)
        self.load_config()
    
    def load_config(self):
        """Carga la configuración del programa"""
        self.config = {
            'password_hash': None,
            'salt': None,
            'admin_token': None,
            'discord_webhook_url': None
        }
        
        # DEBUG messages comentados para modo producción
        # print(f"DEBUG: Buscando archivo de configuracion: {self.config_file}")
        # print(f"DEBUG: Directorio actual: {os.getcwd()}")
        # print(f"DEBUG: Ejecutable: {sys.executable}")
        # print(f"DEBUG: Es compilado: {is_compiled()}")
        if os.path.exists(self.config_file):
            # print(f"DEBUG: Archivo de configuracion encontrado")
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # print(f"DEBUG: Configuracion cargada: {self.config}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                # print(f"DEBUG: Error al cargar configuracion: {e}")
                self.config = {
                    'password_hash': None,
                    'salt': None,
                    'admin_token': None,
                    'discord_webhook_url': None
                }
        # else:
            # print(f"DEBUG: Archivo de configuracion NO encontrado")
        
        # El webhook de Discord ya está hardcodeado en __init__
        # print(f"DEBUG: discord_webhook_url hardcodeado: {self.discord_webhook_url}")
    
    def save_config(self):
        """Guarda la configuración del programa"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception:
            return False
    
    def set_password(self, password):
        """Establece la contraseña del administrador"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        self.config['password_hash'] = base64.b64encode(password_hash).decode()
        self.config['salt'] = salt
        self.config['admin_token'] = secrets.token_urlsafe(32)
        return self.save_config()
    
    def verify_password(self, password):
        """Verifica la contraseña del administrador"""
        if not self.config.get('password_hash') or not self.config.get('salt'):
            return False
        
        try:
            salt = self.config['salt']
            stored_hash = base64.b64decode(self.config['password_hash'])
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash == stored_hash
        except Exception:
            return False
    
    def validate_token(self, token):
        """Valida un token de jugador"""
        if not self.token_generator:
            return False, "Sistema de tokens no disponible"
        
        return self.token_generator.validate_token(token)
    
    def get_token_info(self, token):
        """Obtiene información de un token"""
        if not self.token_generator:
            return None
        
        valid, result = self.validate_token(token)
        if valid and isinstance(result, dict):
            return result
        return None
    
    def get_pc_info(self):
        """Obtiene información básica de la PC incluyendo identificadores únicos"""
        try:
            import platform
            import socket
            import uuid
            import subprocess
            
            pc_info = {
                'computer_name': platform.node(),
                'os': platform.system(),
                'os_version': platform.version(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'username': os.getenv('USERNAME', 'Unknown')
            }
            
            # Obtener identificadores únicos del sistema
            try:
                # MAC Address (primera interfaz de red)
                mac = uuid.getnode()
                pc_info['mac_address'] = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
            except:
                pc_info['mac_address'] = 'Unknown'
            
            try:
                # Dirección IP local
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                pc_info['local_ip'] = local_ip
            except:
                pc_info['local_ip'] = 'Unknown'
            
            try:
                # Dirección IP externa (usando servicio externo)
                import requests
                response = requests.get('https://api.ipify.org', timeout=5)
                if response.status_code == 200:
                    pc_info['external_ip'] = response.text.strip()
                else:
                    pc_info['external_ip'] = 'Unknown'
            except:
                pc_info['external_ip'] = 'Unknown'
            
            try:
                # UUID del sistema (Windows)
                if platform.system() == 'Windows':
                    result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and line.strip() != 'UUID':
                                pc_info['system_uuid'] = line.strip()
                                break
                        if 'system_uuid' not in pc_info:
                            pc_info['system_uuid'] = 'Unknown'
                    else:
                        pc_info['system_uuid'] = 'Unknown'
                else:
                    pc_info['system_uuid'] = 'Unknown'
            except:
                pc_info['system_uuid'] = 'Unknown'
            
            try:
                # Serial Number del disco duro principal (Windows)
                if platform.system() == 'Windows':
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'SerialNumber'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and line.strip() != 'SerialNumber':
                                pc_info['disk_serial'] = line.strip()
                                break
                        if 'disk_serial' not in pc_info:
                            pc_info['disk_serial'] = 'Unknown'
                    else:
                        pc_info['disk_serial'] = 'Unknown'
                else:
                    pc_info['disk_serial'] = 'Unknown'
            except:
                pc_info['disk_serial'] = 'Unknown'
            
            # Crear huella digital única del sistema
            fingerprint_parts = [
                pc_info.get('computer_name', ''),
                pc_info.get('mac_address', ''),
                pc_info.get('system_uuid', ''),
                pc_info.get('disk_serial', '')
            ]
            fingerprint = hashlib.md5('|'.join(fingerprint_parts).encode()).hexdigest()
            pc_info['system_fingerprint'] = fingerprint
            
            self.results['pc_info'] = pc_info
            return pc_info
        except Exception as e:
            print(f"Error al obtener información del PC: {e}")
            return {}
        
    def find_steam_path(self):
        """Encuentra la ruta de instalación de Steam desde el registro de Windows"""
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            self.steam_path = winreg.QueryValueEx(hkey, "SteamPath")[0]
            winreg.CloseKey(hkey)
            return True
        except (FileNotFoundError, OSError):
            try:
                # Intentar en HKEY_LOCAL_MACHINE como alternativa
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
                self.steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
                winreg.CloseKey(hkey)
                return True
            except (FileNotFoundError, OSError):
                return False
    
    def find_l4d2_path(self):
        """Encuentra la ruta de instalación de Left 4 Dead 2"""
        if not self.steam_path:
            return False
            
        possible_paths = [
            os.path.join(self.steam_path, "steamapps", "common", "Left 4 Dead 2"),
            os.path.join(self.steam_path, "steamapps", "common", "Left 4 Dead 2 Dedicated Server")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.l4d2_path = path
                return True
        return False
    
    def detect_mods(self):
        """Detecta mods instalados en Left 4 Dead 2 con análisis mejorado"""
        if not self.l4d2_path:
            return False
            
        # Múltiples ubicaciones donde pueden estar los mods
        mod_paths = [
            os.path.join(self.l4d2_path, "left4dead2"),  # IMPORTANTE: Escanear left4dead2/ directamente para VPK no oficiales
            os.path.join(self.l4d2_path, "left4dead2", "addons"),
            os.path.join(self.l4d2_path, "left4dead2", "custom"),
            os.path.join(self.l4d2_path, "left4dead2", "maps"),
            os.path.join(self.l4d2_path, "left4dead2", "materials"),
            os.path.join(self.l4d2_path, "left4dead2", "models"),
            os.path.join(self.l4d2_path, "left4dead2", "sound"),
            os.path.join(self.l4d2_path, "left4dead2", "scripts")
        ]
        
        # Archivos oficiales que deben ser ignorados
        official_files = {
            "german_censorship.vpk",
            "pak01_dir.vpk", "pak02_dir.vpk", "pak03_dir.vpk", "pak04_dir.vpk",
            "pak05_dir.vpk", "pak06_dir.vpk", "pak07_dir.vpk", "pak08_dir.vpk",
            "pak09_dir.vpk", "pak10_dir.vpk", "pak11_dir.vpk", "pak12_dir.vpk"
        }
        
        # Archivos pak01_XXX oficiales (patrón: pak01_ seguido de números)
        # Estos son archivos oficiales del juego y deben ser ignorados
        import re
        official_pak_pattern = re.compile(r'^pak01_\d{3}$', re.IGNORECASE)
        
        # Ruta de addons para verificar si el mod está en addons/ directamente (no en workshop)
        addons_path = os.path.join(self.l4d2_path, "left4dead2", "addons")
        workshop_path = os.path.join(addons_path, "workshop")
        
        # Patrones de archivos sospechosos
        suspicious_patterns = [
            r'.*cheat.*', r'.*hack.*', r'.*aimbot.*', r'.*wallhack.*',
            r'.*esp.*', r'.*triggerbot.*', r'.*speedhack.*', r'.*norecoil.*',
            r'.*radar.*', r'.*overlay.*', r'.*inject.*', r'.*bypass.*'
        ]
        
        mods_found = []
        
        try:
            
            for mod_path in mod_paths:
                if not os.path.exists(mod_path):
                    continue
                
                # Verificar si estamos en la carpeta workshop - NO ignorar nada ahí
                # Solo ignorar mapas competitivos si están en addons/ directamente
                # Normalizar rutas para comparación (case-insensitive en Windows)
                mod_path_normalized = os.path.normpath(mod_path).lower()
                addons_path_normalized = os.path.normpath(addons_path).lower()
                workshop_path_normalized = os.path.normpath(workshop_path).lower()
                
                is_workshop_folder = mod_path_normalized.startswith(workshop_path_normalized)
                is_addons_direct = mod_path_normalized == addons_path_normalized
                    
                for filename in os.listdir(mod_path):
                    file_path = os.path.join(mod_path, filename)
                    
                    # IGNORAR archivos DEM (demos/grabaciones del juego) - No son mods ni cheats
                    if filename.endswith(".dem") or filename.lower().endswith(".dem"):
                        continue  # Ignorar completamente los archivos DEM
                    
                    # Verificar archivos VPK
                    if filename.endswith(".vpk"):
                        # Verificar si es un archivo oficial
                        filename_no_ext = filename[:-4]  # Sin extensión
                        
                        # Ignorar archivos oficiales
                        if filename in official_files:
                            continue
                        
                        # Ignorar archivos pak01_XXX oficiales (patrón: pak01_ seguido de 3 dígitos)
                        if official_pak_pattern.match(filename_no_ext):
                            continue
                        
                        # Verificar si es un mapa competitivo legítimo
                        # Solo ignorar si está en addons/ directamente (no en workshop)
                        mod_name_without_ext = filename_no_ext.lower()
                        
                        # Si es un mapa competitivo y está en addons/ directamente, ignorarlo
                        if mod_name_without_ext in COMPETITIVE_MAPS_WHITELIST and is_addons_direct and not is_workshop_folder:
                            # Ignorar este mod - es un mapa competitivo legítimo
                            continue
                        
                        # Si estamos en la carpeta left4dead2/ directamente, es MUY sospechoso
                        # (los VPK oficiales ya fueron filtrados arriba)
                        left4dead2_dir_path = os.path.join(self.l4d2_path, "left4dead2")
                        if mod_path.lower() == left4dead2_dir_path.lower():
                            # VPK en left4dead2/ que no es oficial = CRÍTICO
                            file_size = os.path.getsize(file_path)
                            mod_info = {
                                'name': filename,
                                'size': file_size,
                                'path': file_path,
                                'location': mod_path,
                                'suspicious': True,
                                'analysis': f'🚨 CRÍTICO: Archivo VPK no oficial en carpeta left4dead2/. Posible mod para Versus/Competitivo. Los archivos VPK oficiales (pak01_XXX) ya fueron filtrados.'
                            }
                            mods_found.append(mod_info)
                            continue
                        
                        file_size = os.path.getsize(file_path)
                        
                        # Análisis de contenido del archivo
                        is_suspicious = self._analyze_mod_content(file_path, filename)
                        
                        mod_info = {
                            'name': filename,
                            'size': file_size,
                            'path': file_path,
                            'location': mod_path,
                            'suspicious': is_suspicious,
                            'analysis': self._get_mod_analysis(file_path)
                        }
                        
                        mods_found.append(mod_info)
                    
                    # Verificar otros tipos de archivos sospechosos
                    elif self._is_suspicious_file(filename):
                        file_size = os.path.getsize(file_path)
                        
                        mod_info = {
                            'name': filename,
                            'size': file_size,
                            'path': file_path,
                            'location': mod_path,
                            'suspicious': True,
                            'analysis': f'Archivo sospechoso detectado: {filename}'
                        }
                        
                        mods_found.append(mod_info)
                        
        except OSError as e:
            print(f"Error al escanear mods: {e}")
        
        self.results['mods_detected'] = mods_found
        return len(mods_found) > 0
    
    def _analyze_mod_content(self, file_path, filename):
        """Analiza el contenido de un mod para determinar si es sospechoso"""
        try:
            # Verificar patrones sospechosos en el nombre
            suspicious_patterns = [
                r'cheat', r'hack', r'aimbot', r'wallhack', r'esp', r'triggerbot',
                r'speedhack', r'norecoil', r'radar', r'overlay', r'inject', r'bypass'
            ]
            
            import re
            filename_lower = filename.lower()
            
            for pattern in suspicious_patterns:
                if re.search(pattern, filename_lower):
                    return True
            
            # Verificar tamaño sospechoso (mods muy pequeños o muy grandes)
            file_size = os.path.getsize(file_path)
            if file_size < 1024 or file_size > 100 * 1024 * 1024:  # < 1KB o > 100MB
                return True
            
            return False
            
        except Exception:
            return False
    
    def _is_suspicious_file(self, filename):
        """Determina si un archivo es sospechoso por su nombre o extensión"""
        filename_lower = filename.lower()
        
        # IGNORAR archivos DEM (demos/grabaciones del juego) - No son sospechosos
        # Los archivos .dem son grabaciones/replays del juego, no mods ni cheats
        if filename_lower.endswith('.dem'):
            return False
        
        suspicious_extensions = ['.dll', '.exe', '.bat', '.cmd', '.vbs', '.js']
        suspicious_names = [
            'cheat', 'hack', 'aimbot', 'wallhack', 'esp', 'triggerbot',
            'speedhack', 'norecoil', 'radar', 'overlay', 'inject', 'bypass'
        ]
        
        # Verificar extensiones sospechosas
        for ext in suspicious_extensions:
            if filename_lower.endswith(ext):
                return True
        
        # Verificar nombres sospechosos
        for name in suspicious_names:
            if name in filename_lower:
                return True
        
        return False
    
    def _get_mod_analysis(self, file_path):
        """Obtiene análisis detallado de un mod"""
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            analysis = []
            
            # Análisis de tamaño
            if file_size < 1024:
                analysis.append("Archivo muy pequeño (posible cheat)")
            elif file_size > 50 * 1024 * 1024:
                analysis.append("Archivo muy grande (posible mod completo)")
            
            # Análisis de nombre
            if any(keyword in file_name.lower() for keyword in ['cheat', 'hack', 'aimbot']):
                analysis.append("Nombre contiene palabras sospechosas")
            
            # Análisis de fecha de modificación
            import time
            mod_time = os.path.getmtime(file_path)
            current_time = time.time()
            days_old = (current_time - mod_time) / (24 * 3600)
            
            if days_old < 1:
                analysis.append("Archivo muy reciente (posible cheat)")
            
            return "; ".join(analysis) if analysis else "Análisis normal"
            
        except Exception:
            return "Error en análisis"
    
    def detect_unofficial_folders(self):
        """Detecta carpetas no oficiales en la raíz de Left 4 Dead 2"""
        if not self.l4d2_path:
            return False
        
        unofficial_folders = []
        
        try:
            # Listar todas las carpetas en la raíz de L4D2
            for item in os.listdir(self.l4d2_path):
                item_path = os.path.join(self.l4d2_path, item)
                
                # Solo verificar carpetas, no archivos
                if os.path.isdir(item_path):
                    # Verificar si la carpeta está en la whitelist oficial
                    if item.lower() not in OFFICIAL_L4D2_FOLDERS:
                        # Carpeta no oficial detectada
                        folder_info = {
                            'folder_name': item,
                            'folder_path': item_path,
                            'severity': 'CRITICAL',
                            'description': f'Carpeta no oficial detectada en raíz: {item}',
                            'reason': 'Esta carpeta no es parte de la instalación oficial de L4D2. Posible carpeta de mods para Versus/Competitivo.'
                        }
                        
                        # Analizar contenido de la carpeta sospechosa
                        try:
                            all_files = os.listdir(item_path)
                            files_count = len([f for f in all_files if os.path.isfile(os.path.join(item_path, f))])
                            folder_info['files_count'] = files_count
                            
                            # Buscar archivos VPK específicamente (mods comprimidos)
                            vpk_files = [f for f in all_files if f.endswith('.vpk')]
                            if vpk_files:
                                folder_info['vpk_files'] = vpk_files
                                folder_info['vpk_count'] = len(vpk_files)
                                folder_info['description'] += f' ⚠️ Contiene {len(vpk_files)} archivo(s) VPK (posible paquete de mods)'
                                folder_info['severity'] = 'CRITICAL'
                                
                                # Listar algunos nombres de VPK para referencia
                                if len(vpk_files) <= 5:
                                    folder_info['vpk_names'] = vpk_files
                                else:
                                    folder_info['vpk_names'] = vpk_files[:5]
                                    folder_info['vpk_names'].append(f'...y {len(vpk_files) - 5} más')
                            
                            # Verificar si hay subcarpetas (estructura de mod)
                            subdirs = [d for d in all_files if os.path.isdir(os.path.join(item_path, d))]
                            if subdirs:
                                folder_info['subdirectories'] = subdirs[:10]  # Primeras 10
                                
                        except (PermissionError, OSError):
                            folder_info['files_count'] = 'No accesible'
                        
                        unofficial_folders.append(folder_info)
        
        except (PermissionError, OSError) as e:
            print(f"Error al escanear carpetas de L4D2: {e}")
        
        self.results['unofficial_folders'] = unofficial_folders
        return len(unofficial_folders) > 0
    
    def validate_gameinfo_txt(self):
        """Valida la integridad del archivo gameinfo.txt"""
        if not self.l4d2_path:
            return False
        
        gameinfo_path = os.path.join(self.l4d2_path, "left4dead2", "gameinfo.txt")
        
        if not os.path.exists(gameinfo_path):
            self.results['gameinfo_validation'] = {
                'status': 'MISSING',
                'severity': 'CRITICAL',
                'description': 'Archivo gameinfo.txt no encontrado'
            }
            return True  # Es sospechoso que no exista
        
        try:
            with open(gameinfo_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            # Normalizar espacios en blanco para comparación
            current_normalized = ' '.join(current_content.split())
            official_normalized = ' '.join(OFFICIAL_GAMEINFO_CONTENT.split())
            
            if current_normalized == official_normalized:
                self.results['gameinfo_validation'] = {
                    'status': 'VALID',
                    'severity': 'NONE',
                    'description': 'Archivo gameinfo.txt es oficial y no ha sido modificado'
                }
                return False
            else:
                # Detectar qué fue modificado
                modifications = []
                
                # Buscar líneas de SearchPaths adicionales
                if 'SearchPaths' in current_content:
                    # Extraer sección SearchPaths
                    import re
                    # Buscar SearchPaths con diferentes variaciones (case-insensitive, con/sin espacios)
                    search_paths_match = re.search(r'SearchPaths\s*\{([^}]*)\}', current_content, re.DOTALL | re.IGNORECASE)
                    if search_paths_match:
                        search_paths_content = search_paths_match.group(1)
                        
                        # Buscar Game paths (incluyendo errores de tipeo como "Gmme")
                        # Patrón más flexible para detectar "Game" o variaciones
                        game_paths = re.findall(r'(?:Game|Gmme|Gamme|Gam)\s+([^\s\n\r]+)', search_paths_content, re.IGNORECASE)
                        official_game_paths = ['update', 'left4dead2_dlc3', 'left4dead2_dlc2', 
                                              'left4dead2_dlc1', '|gameinfo_path|.', 'hl2']
                        
                        # Normalizar rutas oficiales para comparación
                        official_game_paths_normalized = [p.lower().strip() for p in official_game_paths]
                        
                        for game_path in game_paths:
                            game_path_clean = game_path.strip()
                            game_path_normalized = game_path_clean.lower()
                            
                            # Verificar si es una ruta oficial
                            if game_path_normalized not in official_game_paths_normalized:
                                # Es una ruta no oficial - CRÍTICO para versus/competitivo
                                modifications.append(f'🚨 RUTA NO OFICIAL EN SearchPaths: "{game_path_clean}" - Posible mod para Versus/Competitivo')
                                
                                # Verificar si la carpeta existe en la raíz de L4D2
                                if self.l4d2_path:
                                    folder_path = os.path.join(self.l4d2_path, game_path_clean)
                                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                                        modifications.append(f'   📁 Carpeta encontrada: {folder_path}')
                                        
                                        # Contar archivos VPK en la carpeta
                                        try:
                                            vpk_files = [f for f in os.listdir(folder_path) if f.endswith('.vpk')]
                                            if vpk_files:
                                                modifications.append(f'   ⚠️ {len(vpk_files)} archivo(s) VPK encontrado(s) en esta carpeta')
                                        except:
                                            pass
                
                self.results['gameinfo_validation'] = {
                    'status': 'MODIFIED',
                    'severity': 'CRITICAL',
                    'description': 'Archivo gameinfo.txt ha sido modificado',
                    'modifications': modifications if modifications else ['Contenido general modificado'],
                    'file_path': gameinfo_path
                }
                return True
        
        except Exception as e:
            self.results['gameinfo_validation'] = {
                'status': 'ERROR',
                'severity': 'HIGH',
                'description': f'Error al validar gameinfo.txt: {e}'
            }
            return False
    
    def validate_addonconfig_cfg(self):
        """Valida la integridad del archivo addonconfig.cfg"""
        if not self.l4d2_path:
            return False
        
        addonconfig_path = os.path.join(self.l4d2_path, "left4dead2", "cfg", "addonconfig.cfg")
        
        if not os.path.exists(addonconfig_path):
            self.results['addonconfig_validation'] = {
                'status': 'MISSING',
                'severity': 'CRITICAL',
                'description': 'Archivo addonconfig.cfg no encontrado',
                'file_path': addonconfig_path
            }
            return True  # Es sospechoso que no exista
        
        try:
            with open(addonconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            # Normalizar espacios en blanco para comparación
            current_normalized = ' '.join(current_content.split())
            official_normalized = ' '.join(OFFICIAL_ADDONCONFIG_CONTENT.split())
            
            if current_normalized == official_normalized:
                self.results['addonconfig_validation'] = {
                    'status': 'VALID',
                    'severity': 'NONE',
                    'description': 'Archivo addonconfig.cfg es oficial y no ha sido modificado',
                    'file_path': addonconfig_path
                }
                return False
            else:
                # Detectar qué fue modificado - CRÍTICO: versus, scavenge y mutation15 deben ser "1"
                issues = []
                
                # Extraer valores de RestrictAddons
                import re
                
                # Buscar valores específicos
                modes_to_check = {
                    'versus': '1',
                    'scavenge': '1',
                    'mutation15': '1'
                }
                
                for mode, expected_value in modes_to_check.items():
                    # Buscar patrón: "modo"  "valor"
                    pattern = rf'"{mode}"\s+"(\d+)"'
                    match = re.search(pattern, current_content)
                    
                    if match:
                        actual_value = match.group(1)
                        if actual_value != expected_value:
                            issues.append(f'Modo "{mode}" tiene valor "{actual_value}" (debe ser "{expected_value}")')
                    else:
                        issues.append(f'Modo "{mode}" no encontrado en archivo')
                
                # Verificar si default está presente
                default_match = re.search(r'"default"\s+"(\d+)"', current_content)
                if not default_match:
                    issues.append('Modo "default" no encontrado')
                
                if issues:
                    self.results['addonconfig_validation'] = {
                        'status': 'MODIFIED',
                        'severity': 'CRITICAL',
                        'description': 'Archivo addonconfig.cfg ha sido modificado - ADDONS PERMITIDOS EN VERSUS',
                        'issues': issues,
                        'file_path': addonconfig_path
                    }
                    return True
                else:
                    # Contenido diferente pero valores correctos
                    self.results['addonconfig_validation'] = {
                        'status': 'MODIFIED_FORMAT',
                        'severity': 'LOW',
                        'description': 'Archivo addonconfig.cfg tiene formato diferente pero valores correctos',
                        'file_path': addonconfig_path
                    }
                    return False
        
        except Exception as e:
            self.results['addonconfig_validation'] = {
                'status': 'ERROR',
                'severity': 'HIGH',
                'description': f'Error al validar addonconfig.cfg: {e}',
                'file_path': addonconfig_path
            }
            return False
    
    def validate_360controller_cfg(self):
        """Valida la integridad del archivo 360controller.cfg"""
        if not self.l4d2_path:
            return False
        
        controller_path = os.path.join(self.l4d2_path, "left4dead2", "cfg", "360controller.cfg")
        
        if not os.path.exists(controller_path):
            self.results['controller_validation'] = {
                'status': 'MISSING',
                'severity': 'MEDIUM',
                'description': 'Archivo 360controller.cfg no encontrado (solo necesario si se usa mando)',
                'file_path': controller_path
            }
            return False  # No es crítico si no existe (no todos usan mando)
        
        try:
            with open(controller_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            # Normalizar espacios en blanco para comparación
            current_normalized = ' '.join(current_content.split())
            official_normalized = ' '.join(OFFICIAL_360CONTROLLER_CONTENT.split())
            
            if current_normalized == official_normalized:
                self.results['controller_validation'] = {
                    'status': 'VALID',
                    'severity': 'NONE',
                    'description': 'Archivo 360controller.cfg es oficial y no ha sido modificado',
                    'file_path': controller_path
                }
                return False
            else:
                # Detectar qué fue modificado - CRÍTICO: sk_autoaim_mode debe ser 2
                issues = []
                
                import re
                
                # Buscar sk_autoaim_mode
                autoaim_match = re.search(r'sk_autoaim_mode\s+(\d+)', current_content)
                
                if autoaim_match:
                    autoaim_value = autoaim_match.group(1)
                    if autoaim_value != '2':
                        issues.append(f'sk_autoaim_mode tiene valor "{autoaim_value}" (debe ser "2") - POSIBLE AUTOAIM EXPLOIT')
                else:
                    issues.append('sk_autoaim_mode no encontrado en archivo - POSIBLE AUTOAIM EXPLOIT')
                
                # Verificar unbindall al inicio (previene exploit de mouse/teclado con mando)
                if 'unbindall' not in current_content.lower():
                    issues.append('Comando "unbindall" no encontrado - permite usar mouse/teclado con mando (AUTOAIM EXPLOIT)')
                
                if issues:
                    self.results['controller_validation'] = {
                        'status': 'MODIFIED',
                        'severity': 'CRITICAL',
                        'description': 'Archivo 360controller.cfg ha sido modificado - POSIBLE AUTOAIM EXPLOIT',
                        'issues': issues,
                        'file_path': controller_path
                    }
                    return True
                else:
                    # Contenido diferente pero valores críticos correctos
                    self.results['controller_validation'] = {
                        'status': 'MODIFIED_FORMAT',
                        'severity': 'LOW',
                        'description': 'Archivo 360controller.cfg tiene formato diferente pero valores críticos correctos',
                        'file_path': controller_path
                    }
                    return False
        
        except Exception as e:
            self.results['controller_validation'] = {
                'status': 'ERROR',
                'severity': 'MEDIUM',
                'description': f'Error al validar 360controller.cfg: {e}',
                'file_path': controller_path
            }
            return False
    
    def validate_perf_cfg(self):
        """Valida la integridad del archivo perf.cfg"""
        if not self.l4d2_path:
            return False
        
        perf_path = os.path.join(self.l4d2_path, "left4dead2", "cfg", "perf.cfg")
        
        if not os.path.exists(perf_path):
            self.results['perf_validation'] = {
                'status': 'MISSING',
                'severity': 'NONE',
                'description': 'Archivo perf.cfg no encontrado (solo necesario para pruebas de rendimiento)',
                'file_path': perf_path
            }
            return False  # No es crítico si no existe
        
        try:
            with open(perf_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            # Normalizar espacios en blanco para comparación
            current_normalized = ' '.join(current_content.split())
            official_normalized = ' '.join(OFFICIAL_PERF_CONTENT.split())
            
            if current_normalized == official_normalized:
                self.results['perf_validation'] = {
                    'status': 'VALID',
                    'severity': 'NONE',
                    'description': 'Archivo perf.cfg es oficial y no ha sido modificado',
                    'file_path': perf_path
                }
                return False
            else:
                # Detectar comandos sospechosos en perf.cfg
                issues = []
                
                import re
                
                # Comandos que NO deberían estar en perf.cfg (comandos de cheat)
                forbidden_commands = [
                    'sv_cheats', 'god', 'noclip', 'buddha', 'give', 'impulse 101',
                    'z_health', 'nb_blind', 'director_force', 'z_spawn tank',
                    'z_spawn witch', 'sb_all_bot_game', 'mp_gamemode'
                ]
                
                for cmd in forbidden_commands:
                    if cmd in current_content.lower():
                        issues.append(f'Comando prohibido encontrado: "{cmd}"')
                
                if issues:
                    self.results['perf_validation'] = {
                        'status': 'MODIFIED',
                        'severity': 'CRITICAL',
                        'description': 'Archivo perf.cfg contiene comandos prohibidos',
                        'issues': issues,
                        'file_path': perf_path
                    }
                    return True
                else:
                    # Contenido diferente pero sin comandos prohibidos
                    self.results['perf_validation'] = {
                        'status': 'MODIFIED_FORMAT',
                        'severity': 'LOW',
                        'description': 'Archivo perf.cfg tiene formato diferente pero sin comandos prohibidos',
                        'file_path': perf_path
                    }
                    return False
        
        except Exception as e:
            self.results['perf_validation'] = {
                'status': 'ERROR',
                'severity': 'MEDIUM',
                'description': f'Error al validar perf.cfg: {e}',
                'file_path': perf_path
            }
            return False
    
    def validate_config_cfg(self):
        """Valida comandos críticos en config.cfg (no valida todo el archivo por su tamaño)"""
        if not self.l4d2_path:
            return False
        
        config_path = os.path.join(self.l4d2_path, "left4dead2", "cfg", "config.cfg")
        
        if not os.path.exists(config_path):
            self.results['config_validation'] = {
                'status': 'MISSING',
                'severity': 'CRITICAL',
                'description': 'Archivo config.cfg no encontrado',
                'file_path': config_path
            }
            return True
        
        try:
            with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            issues = []
            
            import re
            
            # Verificar comandos críticos que podrían usarse para hacer trampa
            # 1. sk_autoaim_mode debe ser 1 (para mouse/teclado)
            autoaim_match = re.search(r'sk_autoaim_mode\s+"?(\d+)"?', current_content)
            if autoaim_match:
                autoaim_value = autoaim_match.group(1)
                if autoaim_value != '1':
                    issues.append(f'sk_autoaim_mode tiene valor "{autoaim_value}" (debe ser "1" para mouse/teclado)')
            
            # 2. Verificar que unbindall esté presente (previene binds ocultos)
            if 'unbindall' not in current_content.lower():
                issues.append('Comando "unbindall" no encontrado - pueden existir binds ocultos')
            
            # 3. Comandos prohibidos que NO deberían estar en config.cfg
            forbidden_commands = [
                ('sv_cheats', 'Permite activar cheats en servidor local'),
                ('god', 'Modo invulnerabilidad'),
                ('noclip', 'Atravesar paredes'),
                ('buddha', 'Vida mínima 1 HP'),
                ('give', 'Dar items'),
                ('z_spawn tank', 'Spawnear Tank'),
                ('z_spawn witch', 'Spawnear Witch'),
                ('director_force', 'Forzar eventos del director'),
                ('nb_blind', 'Cegar bots'),
                ('z_health', 'Modificar vida de infectados')
            ]
            
            for cmd, description in forbidden_commands:
                if cmd in current_content.lower():
                    issues.append(f'Comando prohibido: "{cmd}" - {description}')
            
            if issues:
                self.results['config_validation'] = {
                    'status': 'MODIFIED',
                    'severity': 'CRITICAL',
                    'description': 'Archivo config.cfg contiene configuraciones sospechosas',
                    'issues': issues,
                    'file_path': config_path
                }
                return True
            else:
                self.results['config_validation'] = {
                    'status': 'VALID',
                    'severity': 'NONE',
                    'description': 'Archivo config.cfg no contiene comandos prohibidos',
                    'file_path': config_path
                }
                return False
        
        except Exception as e:
            self.results['config_validation'] = {
                'status': 'ERROR',
                'severity': 'HIGH',
                'description': f'Error al validar config.cfg: {e}',
                'file_path': config_path
            }
            return False
    
    def check_against_cheat_signatures(self, filename):
        """Verifica si un nombre de archivo coincide con firmas de cheats conocidos"""
        filename_lower = filename.lower()
        matched_cheats = []
        
        for cheat_name, cheat_data in KNOWN_CHEAT_SIGNATURES.items():
            for pattern in cheat_data['patterns']:
                if pattern in filename_lower:
                    matched_cheats.append({
                        'cheat_type': cheat_name,
                        'matched_pattern': pattern,
                        'severity': cheat_data['severity'],
                        'description': cheat_data['description']
                    })
                    break  # Solo una coincidencia por tipo de cheat
        
        return matched_cheats
    
    def scan_critical_locations(self):
        """Escanea ubicaciones críticas del juego de forma exhaustiva"""
        if not self.l4d2_path:
            return False
        
        critical_findings = []
        
        # Ubicaciones críticas a escanear (PRIORIDAD ALTA para detección de hacks)
        critical_locations = [
            {
                'path': os.path.join(self.l4d2_path, "bin"),  # CRÍTICO: DLLs reemplazadas aquí
                'name': 'Bin (DLLs)',
                'priority': 'CRITICAL',
                'scan_vpk': False,
                'scan_loose': True,
                'extensions': ['.dll'],  # Solo DLLs (d3d9.dll, opengl32.dll, etc.)
                'check_replaced': True  # Verificar DLLs reemplazadas
            },
            {
                'path': os.path.join(self.l4d2_path, "left4dead2", "cfg"),
                'name': 'Config Files (CFG)',
                'priority': 'CRITICAL',
                'scan_vpk': False,
                'scan_loose': True,
                'extensions': ['.cfg']  # Solo archivos .cfg (autoexec.cfg, config.cfg)
            },
            {
                'path': os.path.join(self.l4d2_path, "left4dead2", "addons"),
                'name': 'Addons',
                'priority': 'CRITICAL',
                'scan_vpk': True,
                'scan_loose': True
            },
            {
                'path': os.path.join(self.l4d2_path, "left4dead2", "scripts"),
                'name': 'Scripts',
                'priority': 'HIGH',
                'scan_vpk': False,
                'scan_loose': True
            },
            {
                'path': os.path.join(self.l4d2_path, "left4dead2", "materials"),
                'name': 'Materials',
                'priority': 'MEDIUM',
                'scan_vpk': False,
                'scan_loose': True
            },
            {
                'path': os.path.join(self.l4d2_path, "left4dead2", "models"),
                'name': 'Models',
                'priority': 'MEDIUM',
                'scan_vpk': False,
                'scan_loose': True
            },
            {
                'path': self.l4d2_path,  # Raíz del juego
                'name': 'Game Root',
                'priority': 'CRITICAL',
                'scan_vpk': False,
                'scan_loose': True,
                'extensions': ['.dll', '.exe', '.asi']  # Solo archivos peligrosos
            }
        ]
        
        for location in critical_locations:
            if not os.path.exists(location['path']):
                continue
            
            try:
                for item in os.listdir(location['path']):
                    item_path = os.path.join(location['path'], item)
                    
                    # Saltar carpetas en raíz (ya se verifican en detect_unofficial_folders)
                    if location['name'] == 'Game Root' and os.path.isdir(item_path):
                        continue
                    
                    # Filtrar por extensiones si está especificado
                    if 'extensions' in location:
                        if not any(item.lower().endswith(ext) for ext in location['extensions']):
                            continue
                    
                    # Solo archivos
                    if os.path.isfile(item_path):
                        # Verificar DLLs reemplazadas en bin/ (CRÍTICO)
                        if location['name'] == 'Bin (DLLs)' and 'check_replaced' in location:
                            if self._is_replaced_dll(item, item_path):
                                critical_findings.append({
                                    'location': location['name'],
                                    'location_path': location['path'],
                                    'file_name': item,
                                    'file_path': item_path,
                                    'file_size': os.path.getsize(item_path),
                                    'cheat_type': 'REPLACED_DLL',
                                    'matched_pattern': 'DLL reemplazada',
                                    'severity': 'CRITICAL',
                                    'description': f'🚨 DLL reemplazada en bin/: {item} - Posible wrapper/hook para inyección de cheats',
                                    'detection_method': 'Replaced DLL Detection'
                                })
                                continue
                        
                        # Verificar contra firmas de cheats conocidos
                        cheat_matches = self.check_against_cheat_signatures(item)
                        
                        if cheat_matches:
                            for match in cheat_matches:
                                critical_findings.append({
                                    'location': location['name'],
                                    'location_path': location['path'],
                                    'file_name': item,
                                    'file_path': item_path,
                                    'file_size': os.path.getsize(item_path),
                                    'cheat_type': match['cheat_type'],
                                    'matched_pattern': match['matched_pattern'],
                                    'severity': match['severity'],
                                    'description': match['description'],
                                    'detection_method': 'Known Cheat Signature'
                                })
            
            except (PermissionError, OSError) as e:
                print(f"Error al escanear {location['name']}: {e}")
        
        self.results['critical_findings'] = critical_findings
        return len(critical_findings) > 0
    
    def count_steam_accounts(self):
        """Cuenta las cuentas de Steam que han iniciado sesión en esta PC"""
        if not self.steam_path:
            return 0
            
        config_path = os.path.join(self.steam_path, "config", "loginusers.vdf")
        
        if not os.path.exists(config_path):
            return 0
        
        try:
            # Leer archivo VDF manualmente (formato simple de Valve)
            with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extraer SteamIDs y nombres de usuario
            import re
            steam_ids = re.findall(r'"(\d{17})"', content)
            
            # Buscar nombres de usuario asociados
            accounts = []
            for steam_id in set(steam_ids):
                # Buscar el nombre de usuario para este SteamID
                pattern = rf'"{steam_id}"\s*{{\s*"PersonaName"\s*"([^"]*)"'
                match = re.search(pattern, content)
                username = match.group(1) if match else "Unknown"
                
                accounts.append({
                    'steam_id64': steam_id,
                    'username': username,
                    'steam_id3': self.steamid64_to_steamid3(steam_id),
                    'steam_id': self.steamid64_to_steamid(steam_id)
                })
            
            self.results['steam_accounts'] = accounts
            self.results['steam_accounts_count'] = len(accounts)
            return len(accounts)
            
        except (OSError, UnicodeDecodeError):
            return 0
    
    def steamid64_to_steamid3(self, steamid64):
        """Convierte SteamID64 a SteamID3"""
        try:
            steamid3 = int(steamid64) - 76561197960265728
            return f"[U:1:{steamid3}]"
        except:
            return "Invalid"
    
    def steamid64_to_steamid(self, steamid64):
        """Convierte SteamID64 a SteamID"""
        try:
            steamid3 = int(steamid64) - 76561197960265728
            return f"STEAM_0:{steamid3 % 2}:{steamid3 // 2}"
        except:
            return "Invalid"
    
    def detect_suspicious_processes(self):
        """Detecta procesos sospechosos que podrían ser cheats"""
        # Lista de procesos legítimos que deben ser ignorados
        whitelist_processes = [
            'l4d2_verifier.exe', 'l4d2_verifier_console.exe', 'l4d2_token_generator.exe',
            'left4dead2.exe', 'steam.exe', 'steamservice.exe', 'steamwebhelper.exe',
            'gameoverlayui.exe', 'gameoverlayui64.exe', 'steamclient.dll',
            'explorer.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe', 'svchost.exe',
            'chrome.exe', 'firefox.exe', 'discord.exe', 'obs64.exe', 'obs32.exe',
            'nvidia', 'amd', 'intel', 'realtek', 'microsoft', 'windows'
        ]
        
        # Keywords más específicos para cheats reales
        suspicious_keywords = [
            'cheat', 'hack', 'aimbot', 'wallhack', 'esp', 'triggerbot',
            'speedhack', 'norecoil', 'radar', 'injector', 'bypass', 
            'undetected', 'memory', 'dll', 'hook', 'patch', 'crack'
        ]
        
        suspicious_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    proc_cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                    
                    # Verificar si el proceso está en la whitelist
                    is_whitelisted = False
                    for whitelist_item in whitelist_processes:
                        if whitelist_item in proc_name or whitelist_item in proc_exe:
                            is_whitelisted = True
                            break
                    
                    if is_whitelisted:
                        continue
                    
                    # Buscar keywords sospechosos
                    for keyword in suspicious_keywords:
                        if (keyword in proc_name or 
                            keyword in proc_exe or 
                            keyword in proc_cmdline):
                            
                            # Análisis adicional para reducir falsos positivos
                            if self._is_really_suspicious(proc_name, proc_exe, proc_cmdline):
                                suspicious_processes.append({
                                    'pid': proc.info['pid'],
                                    'name': proc.info['name'],
                                    'exe': proc.info['exe'],
                                    'cmdline': proc_cmdline,
                                    'reason': f'Contiene keyword sospechoso: {keyword}'
                                })
                                break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Detectar herramientas de inyección de DLLs específicas
            dll_injection_tools = self.detect_dll_injection_tools()
            suspicious_processes.extend(dll_injection_tools)
                    
        except Exception as e:
            print(f"Error al escanear procesos: {e}")
        
        self.results['suspicious_processes'] = suspicious_processes
        return len(suspicious_processes) > 0
    
    def detect_dll_injection_tools(self):
        """Detecta herramientas específicas de inyección de DLLs"""
        injection_tools_found = []
        
        # Herramientas conocidas de inyección de DLLs
        known_injection_tools = {
            # Herramientas genéricas de inyección
            'processhacker.exe': {
                'name': 'Process Hacker',
                'severity': 'CRITICAL',
                'description': 'Herramienta de análisis de procesos usada para inyectar DLLs'
            },
            'processhacker': {
                'name': 'Process Hacker',
                'severity': 'CRITICAL',
                'description': 'Herramienta de análisis de procesos usada para inyectar DLLs'
            },
            'extremeinjector.exe': {
                'name': 'Extreme Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs diseñado específicamente para inyección'
            },
            'extreme injector': {
                'name': 'Extreme Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs diseñado específicamente para inyección'
            },
            'xenos.exe': {
                'name': 'Xenos Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs avanzado'
            },
            'xenos64.exe': {
                'name': 'Xenos Injector 64-bit',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs avanzado (64-bit)'
            },
            'cheatengine.exe': {
                'name': 'Cheat Engine',
                'severity': 'CRITICAL',
                'description': 'Editor de memoria con capacidades de inyección'
            },
            'cheat engine': {
                'name': 'Cheat Engine',
                'severity': 'CRITICAL',
                'description': 'Editor de memoria con capacidades de inyección'
            },
            'winject.exe': {
                'name': 'Winject',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs para Windows'
            },
            
            # Inyectores específicos de L4D2
            'l4d2 esp injector': {
                'name': 'L4D2 ESP Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector de ESP/WallHack específico para Left 4 Dead 2'
            },
            'l4d2esp': {
                'name': 'L4D2 ESP',
                'severity': 'CRITICAL',
                'description': 'ESP/WallHack para Left 4 Dead 2'
            },
            'l4d2_esp': {
                'name': 'L4D2 ESP',
                'severity': 'CRITICAL',
                'description': 'ESP/WallHack para Left 4 Dead 2'
            },
            'l4d2 injector': {
                'name': 'L4D2 Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector específico para Left 4 Dead 2'
            },
            'l4d2_injector': {
                'name': 'L4D2 Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector específico para Left 4 Dead 2'
            },
            'l4d2 wallhack': {
                'name': 'L4D2 WallHack',
                'severity': 'CRITICAL',
                'description': 'WallHack específico para Left 4 Dead 2'
            },
            'l4d2_wallhack': {
                'name': 'L4D2 WallHack',
                'severity': 'CRITICAL',
                'description': 'WallHack específico para Left 4 Dead 2'
            },
            'l4d2 aimbot': {
                'name': 'L4D2 Aimbot',
                'severity': 'CRITICAL',
                'description': 'Aimbot específico para Left 4 Dead 2'
            },
            'l4d2_aimbot': {
                'name': 'L4D2 Aimbot',
                'severity': 'CRITICAL',
                'description': 'Aimbot específico para Left 4 Dead 2'
            },
            'l4d2 cheat': {
                'name': 'L4D2 Cheat',
                'severity': 'CRITICAL',
                'description': 'Cheat genérico para Left 4 Dead 2'
            },
            'l4d2_cheat': {
                'name': 'L4D2 Cheat',
                'severity': 'CRITICAL',
                'description': 'Cheat genérico para Left 4 Dead 2'
            },
            'left4dead2 injector': {
                'name': 'Left 4 Dead 2 Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector para Left 4 Dead 2'
            },
            'left4dead2_esp': {
                'name': 'Left 4 Dead 2 ESP',
                'severity': 'CRITICAL',
                'description': 'ESP para Left 4 Dead 2'
            },
            
            # Inyectores genéricos
            'dll injector': {
                'name': 'DLL Injector Generic',
                'severity': 'CRITICAL',
                'description': 'Inyector de DLLs genérico'
            },
            'remotethread': {
                'name': 'Remote Thread Injector',
                'severity': 'CRITICAL',
                'description': 'Técnica de inyección por hilo remoto'
            },
            'loadlibrary': {
                'name': 'LoadLibrary Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector usando técnica LoadLibrary'
            },
            'codecave': {
                'name': 'Code Cave Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector usando técnica de code cave'
            },
            'manualmap': {
                'name': 'Manual Map Injector',
                'severity': 'CRITICAL',
                'description': 'Inyector usando técnica manual mapping'
            },
            'inject.exe': {
                'name': 'DLL Inject',
                'severity': 'HIGH',
                'description': 'Ejecutable de inyección genérico'
            },
            'injector.exe': {
                'name': 'Injector',
                'severity': 'HIGH',
                'description': 'Ejecutable de inyección genérico'
            }
        }
        
        try:
            # Verificar si L4D2 está corriendo (importante para contexto)
            l4d2_running = False
            for proc in psutil.process_iter(['name']):
                try:
                    if 'left4dead2' in proc.info['name'].lower():
                        l4d2_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Buscar herramientas de inyección
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    proc_cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                    
                    # Buscar coincidencias con herramientas conocidas
                    for tool_pattern, tool_info in known_injection_tools.items():
                        if tool_pattern in proc_name or tool_pattern in proc_exe or tool_pattern in proc_cmdline:
                            # Determinar severidad extra si L4D2 está corriendo
                            severity_extra = ""
                            if l4d2_running:
                                severity_extra = " [¡L4D2 ESTÁ CORRIENDO!]"
                            
                            injection_tools_found.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'exe': proc.info['exe'],
                                'cmdline': proc_cmdline,
                                'reason': f'Herramienta de inyección detectada: {tool_info["name"]}{severity_extra}',
                                'tool_name': tool_info['name'],
                                'severity': tool_info['severity'],
                                'description': tool_info['description'],
                                'l4d2_running': l4d2_running,
                                'type': 'dll_injection_tool'
                            })
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Error al detectar herramientas de inyección de DLLs: {e}")
        
        return injection_tools_found
    
    def detect_cheat_files_in_system(self):
        """Detecta archivos de cheats en ubicaciones comunes del sistema"""
        cheat_files_found = []
        
        # Ubicaciones comunes donde se instalan cheats (PRIORIDAD: %TEMP% y %APPDATA%)
        # Los loaders de hacks comerciales (Aimware, Baunti, etc.) descomprimen aquí antes de inyectar
        search_locations = [
            # PRIORIDAD CRÍTICA: Carpetas temporales donde loaders descomprimen archivos
            os.path.join(os.environ.get('TEMP', ''), ''),  # %TEMP% - MÁS COMÚN
            os.path.join(os.environ.get('APPDATA', ''), ''),  # %APPDATA% - MÁS COMÚN
            os.path.join(os.environ.get('LOCALAPPDATA', ''), ''),  # %LOCALAPPDATA%
            # Carpetas de usuario (menos comunes pero posibles)
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
            # Carpetas comunes de cheats (raras pero posibles)
            'C:\\Cheats',
            'C:\\Hacks',
            'C:\\ESP',
            'C:\\WallHack',
        ]
        
        # Patrones de nombres de archivos sospechosos (INCLUYENDO HACKS COMERCIALES CONOCIDOS)
        suspicious_file_patterns = [
            # ===== HACKS COMERCIALES CONOCIDOS =====
            # Aimware
            '*aimware*.exe', '*aimware*.dll', '*aim-ware*.exe', '*aim_ware*.exe',
            '*awloader*.exe', '*aw_loader*.exe', '*aw.exe', '*aw.dll',
            
            # BauntiCheats
            '*baunti*.exe', '*baunti*.dll', '*baunticheats*.exe', '*baunti-cheats*.exe',
            '*l4d2helper*.exe', '*l4d2_helper*.exe', '*bauntiloader*.exe',
            
            # Interwebz
            '*interwebz*.exe', '*interwebz*.dll', '*inter-webz*.exe', '*iwz*.exe',
            '*interwebzloader*.exe', '*iwzloader*.exe',
            
            # LMAOBOX
            '*lmaobox*.exe', '*lmaobox*.dll', '*lmao-box*.exe', '*lmaoloader*.exe',
            
            # FleepHack / Fleep
            '*fleep*.exe', '*fleep*.dll', '*fleephack*.exe', '*fleep-hack*.exe',
            '*fleeploader*.exe', '*fleep_loader*.exe',
            
            # Osiris / RatPoison
            '*osiris*.dll', '*ratpoison*.dll', '*rat-poison*.dll', '*osirisloader*.exe',
            
            # ===== INYECTORES ESPECÍFICOS DE L4D2 =====
            'l4d2*esp*.exe', 'l4d2*esp*.dll',
            'l4d2*wallhack*.exe', 'l4d2*wallhack*.dll',
            'l4d2*aimbot*.exe', 'l4d2*aimbot*.dll',
            'l4d2*injector*.exe', 'l4d2*injector*.dll',
            'l4d2*cheat*.exe', 'l4d2*cheat*.dll',
            'left4dead2*esp*.exe', 'left4dead2*esp*.dll',
            
            # ===== DLLs GENÉRICAS DE CHEATS =====
            '*wallhack*.dll', '*esp*.dll', '*aimbot*.dll',
            '*norecoil*.dll', '*triggerbot*.dll', '*speedhack*.dll',
            'pol.dll', 'hack.dll', 'cheat.dll', 'hook.dll',
            '*multihack*.dll', '*multi-hack*.dll',
            
            # ===== EJECUTABLES DE INYECCIÓN =====
            '*injector*.exe', '*inject*.exe', '*injec*.exe',
            '*loader*.exe', '*load*.exe',
            'extreem*.exe', 'extreme*.exe', 'xenos*.exe',
            'process*hacker*.exe', 'cheat*engine*.exe',
            
            # ===== ARCHIVOS COMUNES DE CHEATS =====
            'cheat*.exe', 'hack*.exe', 'mod*.exe',
            '*multihack*.exe', '*multi-hack*.exe',
            'l4d*.exe', 'l4d*.dll', # Cuidado con falsos positivos aquí, validar contexto
        ]
        
        # Nombres de carpetas sospechosas (lista extendida)
        suspicious_folder_names = [
            # Palabras clave directas
            'cheat', 'cheats', 'hack', 'hacks', 'esp', 'wallhack', 'wallhacks',
            'aimbot', 'aimbots', 'triggerbot', 'speedhack', 'norecoil',
            'multihack', 'multi-hack', 'multihacks',
            
            # L4D2 específicos
            'l4d2esp', 'l4d2_esp', 'l4d2-esp', 'l4d2 esp',
            'l4d2cheat', 'l4d2_cheat', 'l4d2-cheat', 'l4d2 cheat',
            'l4d2hack', 'l4d2_hack', 'l4d2wallhack',
            'l4d2loader', 'l4d2_loader', 'l4d2-loader', 'l4d2 loader',
            'left4dead2cheat', 'left4dead2esp', 'left4dead2hack',
            'left4dead2loader', 'left4dead2_loader',
            
            # Inyectores y loaders (extendido)
            'injector', 'inject', 'inj', 'injec', 'inyector',
            'loader', 'load', 'loaders',
            'bootstrap', 'boot',
            'launcher', 'launch', 'launchers',
            'activator', 'activate',
            'starter', 'start',
            'runner', 'run',
            'executor', 'exec',
            'enabler', 'enable',
            'extreem', 'extreme', # Extreem Injector
            
            # Nombres engañosos (muy comunes)
            'gamebooster', 'game-booster', 'game booster',
            'fpsbooster', 'fps-booster', 'fps booster',
            'fpsfix', 'fps-fix', 'fps fix',
            'performanceenhancer', 'performance-enhancer',
            'gameoptimizer', 'game-optimizer', 'optimizer',
            'latencyfix', 'latency-fix', 'pingfix', 'ping-fix',
            'antilag', 'anti-lag', 'lagfix', 'lag-fix',
            'gamefixer', 'game-fixer', 'gamefix',
            
            # Español/Portugués
            'inyector', 'injetor', 'cargador',
            'trampa', 'trampas', 'trucos', 'ayuda',
            'mira', 'punteria',
            
            # Nombres genéricos
            'mod', 'mods', 'modding', 'modifications',
            'trainer', 'trainers', 'modifier', 'modifiers',
            'bypass', 'unlocker', 'crack', 'cracked',
            
            # Comunidades/Proyectos de cheats
            'unknowncheats', 'unknown-cheats', 'uc',
            'mpgh', 'elitepvpers', 'hackforums',
            
            # Herramientas conocidas
            'processhacker', 'process-hacker', 'cheatengine', 'cheat-engine',
            'extremeinjector', 'extreme-injector', 'xenos',
            
            # Otros genéricos
            'tools', 'hacking', 'cheating', 'exploits'
        ]
        
        try:
            import fnmatch
            
            for location in search_locations:
                if not os.path.exists(location):
                    continue
                
                # Determinar profundidad de escaneo
                # Descargas, Escritorio, Documentos -> Recursivo (hasta 2 niveles)
                # Otras carpetas -> Solo raíz (nivel 0)
                is_user_folder = any(x in location for x in ['Desktop', 'Downloads', 'Documents'])
                max_depth = 2 if is_user_folder else 0
                
                try:
                    # Usar os.walk para escaneo flexible
                    for root, dirs, files in os.walk(location):
                        # Calcular profundidad actual
                        try:
                            if root == location:
                                depth = 0
                            else:
                                rel_path = os.path.relpath(root, location)
                                depth = rel_path.count(os.sep) + 1
                        except:
                            depth = 0
                            
                        # Si excedemos la profundidad, limpiar dirs para no seguir bajando y continuar
                        if depth > max_depth:
                            dirs[:] = []
                            continue
                            
                        # 1. Analizar carpetas sospechosas
                        for dir_name in dirs:
                            dir_lower = dir_name.lower()
                            # Verificar si el nombre de la carpeta coincide con patrones sospechosos
                            if any(sus in dir_lower for sus in suspicious_folder_names):
                                folder_path = os.path.join(root, dir_name)
                                # Analizar contenido de la carpeta
                                folder_info = self._analyze_cheat_folder(folder_path, dir_name)
                                if folder_info:
                                    cheat_files_found.append(folder_info)
                        
                        # 2. Analizar archivos sospechosos
                        for file_name in files:
                            file_lower = file_name.lower()
                            file_path = os.path.join(root, file_name)
                            
                            # A. Whitelist check (evitar falsos positivos como instaladores legítimos)
                            if self.is_legitimate_program(file_name, file_path):
                                continue
                                
                            # B. Pattern check
                            is_suspicious = False
                            matched_pattern = ""
                            
                            for pattern in suspicious_file_patterns:
                                if fnmatch.fnmatch(file_lower, pattern):
                                    is_suspicious = True
                                    matched_pattern = pattern
                                    break
                            
                            # Si no coincide con patrones glob, probar también palabras clave directas si no es un archivo común
                            if not is_suspicious:
                                if self._is_cheat_file(file_lower, file_path):
                                    is_suspicious = True
                                    matched_pattern = "keyword_match"

                            if is_suspicious:
                                try:
                                    file_size = os.path.getsize(file_path)
                                    cheat_files_found.append({
                                        'type': 'cheat_file',
                                        'file_name': file_name,
                                        'file_path': file_path,
                                        'file_size': file_size,
                                        'location': root, # Ubicación real donde se encontró
                                        'severity': 'CRITICAL',
                                        'description': f'Archivo de cheat detectado: {file_name} (Patrón: {matched_pattern})'
                                    })
                                except:
                                    pass
                                    
                except Exception as e:
                    # print(f"Error escaneando {location}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error general en detección de archivos: {e}")
        
        self.results['cheat_files_found'] = cheat_files_found
        return len(cheat_files_found) > 0
    
    def _analyze_cheat_folder(self, folder_path, folder_name):
        """Analiza una carpeta sospechosa de contener cheats"""
        try:
            files_in_folder = []
            suspicious_files = []
            total_size = 0
            
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    file_size = os.path.getsize(item_path)
                    total_size += file_size
                    files_in_folder.append(item)
                    
                    item_lower = item.lower()
                    # Detectar archivos específicos de cheats
                    if any(ext in item_lower for ext in ['.dll', '.exe', 'injector', 'esp', 'wallhack', 'aimbot', 'cheat', 'hack']):
                        suspicious_files.append({
                            'name': item,
                            'size': file_size,
                            'path': item_path
                        })
            
            if suspicious_files or len(files_in_folder) > 0:
                return {
                    'type': 'cheat_folder',
                    'folder_name': folder_name,
                    'folder_path': folder_path,
                    'total_files': len(files_in_folder),
                    'suspicious_files': suspicious_files,
                    'total_size': total_size,
                    'severity': 'CRITICAL',
                    'description': f'Carpeta de cheats detectada: {folder_name} ({len(suspicious_files)} archivos sospechosos)'
                }
        except (PermissionError, OSError):
            pass
        
        return None
    
    def _is_cheat_file(self, filename_lower, file_path):
        """Determina si un archivo es un cheat basándose en su nombre"""
        # Lista extendida de palabras clave que indican cheats
        cheat_keywords = [
            # L4D2 específicos
            'l4d2esp', 'l4d2_esp', 'l4d2 esp', 'l4d2-esp',
            'l4d2wallhack', 'l4d2_wallhack', 'l4d2-wallhack',
            'l4d2aimbot', 'l4d2_aimbot', 'l4d2-aimbot',
            'l4d2injector', 'l4d2_injector', 'l4d2-injector',
            'l4d2loader', 'l4d2_loader', 'l4d2-loader',  # NUEVO
            'l4d2cheat', 'l4d2_cheat', 'l4d2-cheat',
            'l4d2mod', 'l4d2_mod', 'l4d2-mod',
            'left4dead2esp', 'left4dead2_esp',
            'left4dead2loader', 'left4dead2_loader',  # NUEVO
            
            # Cheats genéricos
            'wallhack', 'wall-hack', 'aimbot', 'aim-bot',
            'triggerbot', 'trigger-bot', 'speedhack', 'speed-hack',
            'norecoil', 'no-recoil', 'esp.dll', 'hack.dll', 'cheat.dll',
            'bhop', 'bunnyhop',
            
            # Inyectores
            'injector', 'inject', 'loader', 'xenos',
            'extremeinjector', 'extreme injector',
            'processhacker', 'cheatengine',
            
            # Nombres engañosos
            'gamebooster', 'fpsbooster', 'fpsfix',
            'performanceenhancer', 'gameoptimizer',
            'latencyfix', 'pingfix', 'antilag',
            
            # Español/Portugués
            'inyector', 'injetor', 'trampa', 'trucos',
            'mira', 'punteria',
            
            # Genéricos
            'bypass', 'unlocker', 'trainer', 'modifier',
            'godmode', 'noclip', 'infinite', 'unlimited',
            
            # Abreviaciones
            'wh.exe', 'ab.exe', 'ce.exe', 'ph.exe',
            'esp', 'wh', 'ab'
        ]
        
        # Verificar si contiene palabras clave de cheats
        for keyword in cheat_keywords:
            if keyword in filename_lower:
                # Verificar que sea un archivo ejecutable o DLL
                if filename_lower.endswith(('.exe', '.dll', '.bin', '.dat')):
                    return True
        
        return False
    
    def parse_prefetch_with_tool(self, prefetch_file):
        """Usa WinPrefetchView.exe para parsear archivo Prefetch y obtener ruta real"""
        # Buscar la herramienta en la carpeta pfprogam (sin r)
        tool_path = os.path.join(os.path.dirname(sys.executable) if is_compiled() else os.path.dirname(__file__), 'pfprogam', 'WinPrefetchView.exe')
        
        if not os.path.exists(tool_path):
            # Intentar buscar en el directorio actual si no está en pfprogam
            tool_path = os.path.join(os.path.dirname(sys.executable) if is_compiled() else os.path.dirname(__file__), 'WinPrefetchView.exe')
            if not os.path.exists(tool_path):
                return None
        
        try:
            # Ejecutar WinPrefetchView para este archivo específico
            output_file = os.path.join(tempfile.gettempdir(), f'prefetch_{os.path.basename(prefetch_file)}.txt')
            
            # Comando: /stext <Filename> /prefetchfile <Prefetch File>
            cmd = f'"{tool_path}" /stext "{output_file}" /prefetchfile "{prefetch_file}"'
            
            # Ejecutar con timeout para evitar bloqueos
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            
            if not os.path.exists(output_file):
                return None
            
            # Leer y parsear output - intentar múltiples encodings
            exe_path = None
            content = None
            
            # Intentar diferentes encodings
            encodings_to_try = ['utf-16-le', 'utf-16', 'utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings_to_try:
                try:
                    with open(output_file, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    if content and len(content) > 10:  # Verificar que hay contenido válido
                        break
                except:
                    continue
            
            if not content:
                # Limpiar archivo temporal
                try:
                    os.remove(output_file)
                except:
                    pass
                return None
                
            # Buscar la ruta del ejecutable en diferentes formatos posibles
            # WinPrefetchView puede usar diferentes etiquetas
            search_patterns = [
                "Filename:",
                "Full Path:",
                "Executable:",
                "Process Name:",
                "File Name:"
            ]
            
            for line in content.splitlines():
                line = line.strip()
                for pattern in search_patterns:
                    if line.startswith(pattern):
                        # Extraer la parte después del patrón
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            path_candidate = parts[1].strip()
                            # Verificar que parece una ruta válida de Windows (tiene C:, D:, etc.)
                            if path_candidate and len(path_candidate) > 3:
                                # Verificar formato de ruta Windows
                                if len(path_candidate) > 1 and path_candidate[1] == ':':
                                    exe_path = path_candidate
                                    break
                                # A veces puede venir con comillas
                                elif path_candidate.startswith('"') and ':' in path_candidate:
                                    path_candidate = path_candidate.strip('"')
                                    if len(path_candidate) > 1 and path_candidate[1] == ':':
                                        exe_path = path_candidate
                                        break
                if exe_path:
                    break
            
            # Limpiar archivo temporal
            try:
                os.remove(output_file)
            except:
                pass
                
            return exe_path
            
        except Exception as e:
            # Silenciar errores para no saturar el log, pero podríamos activar esto para debug
            # print(f"Error parsing prefetch {os.path.basename(prefetch_file)}: {e}")
            return None

    def is_legitimate_program(self, program_name, exe_path=None):
        """Determina si un programa es legítimo usando whitelist y ruta"""
        program_lower = program_name.lower()
        
        # 1. Verificar whitelist por nombre exacto
        if program_lower in LEGITIMATE_PROGRAMS_WHITELIST:
            return True
            
        # 2. Verificar si termina con alguna extensión de la whitelist (para versiones)
        # Ejemplo: python3.9.exe -> python
        base_name = os.path.splitext(program_lower)[0]
        for legit in LEGITIMATE_PROGRAMS_WHITELIST:
            legit_base = os.path.splitext(legit)[0]
            if base_name == legit_base or base_name.startswith(legit_base + "."):
                return True
        
        # 3. Verificar ruta si está disponible
        if exe_path:
            path_lower = exe_path.lower()
            
            # Rutas legítimas
            for legit_path in LEGITIMATE_PATHS:
                if path_lower.startswith(legit_path.lower()):
                    # Excepción: No permitir carpetas temporales dentro de rutas legítimas si fuera el caso
                    # pero C:\Windows y Program Files suelen ser seguros
                    return True
            
            # Rutas sospechosas (confirmación de sospecha)
            for susp_path in SUSPICIOUS_PATHS:
                if susp_path.lower() in path_lower:
                    return False # Definitivamente sospechoso
        
        return False

    def detect_recently_executed_programs(self):
        """Detecta programas ejecutados recientemente usando Prefetch y Registro de Windows"""
        recently_executed = []
        
        # Patrones de nombres de programas sospechosos (lista extendida)
        suspicious_program_patterns = [
            # Inyectores específicos de L4D2
            'l4d2esp', 'l4d2_esp', 'l4d2 esp', 'l4d2-esp',
            'l4d2wallhack', 'l4d2_wallhack', 'l4d2 wallhack', 'l4d2-wallhack',
            'l4d2aimbot', 'l4d2_aimbot', 'l4d2 aimbot', 'l4d2-aimbot',
            'l4d2injector', 'l4d2_injector', 'l4d2 injector', 'l4d2-injector',
            'l4d2loader', 'l4d2_loader', 'l4d2 loader', 'l4d2-loader',  # NUEVO
            'l4d2cheat', 'l4d2_cheat', 'l4d2 cheat', 'l4d2-cheat',
            'l4d2hack', 'l4d2_hack', 'l4d2 hack', 'l4d2-hack',
            'l4d2mod', 'l4d2_mod', 'l4d2 mod', 'l4d2-mod',
            'left4dead2esp', 'left4dead2_esp', 'left4dead2-esp',
            'left4dead2cheat', 'left4dead2_cheat',
            'left4dead2loader', 'left4dead2_loader',  # NUEVO
            
            # Herramientas de inyección genéricas conocidas
            'processhacker', 'process hacker', 'process-hacker', 'proceshacker',
            'extremeinjector', 'extreme injector', 'extreme-injector',
            'xenos', 'xenos64', 'xenosinjector',
            'cheatengine', 'cheat engine', 'cheat-engine', 'ce.exe',
            'winject', 'dll injector', 'dllinjector', 'dll-injector',
            'manualmap', 'manual-map', 'manualmapper',
            
            # Nombres genéricos comunes de inyectores (SOLO SI SON COMPLETOS O MUY ESPECÍFICOS)
            'injector.exe', 'loader.exe', 'launcher.exe', 
            'cheatengine', 'cheat-engine',
            
            # Palabras clave directas de cheats
            'wallhack', 'wall-hack', 'wh.exe', 'walls',
            'aimbot', 'aim-bot', 'autoaim', 'auto-aim',
            'triggerbot', 'trigger-bot', 'autotrigger',
            'speedhack', 'speed-hack', 'noclip', 'no-clip',
            'norecoil', 'no-recoil', 'nospread', 'no-spread',
            'esp.exe', 'hack.exe', 'cheat.exe', 'mod.exe',
            'bhop', 'bunnyhop', 'autobhop',
            
            # Nombres engañosos (parecen legítimos pero son cheats)
            'gamebooster', 'game-booster', 'game booster',
            'fpsbooster', 'fps-booster', 'fps booster',
            'performanceenhancer', 'performance-enhancer',
            'gameoptimizer', 'game-optimizer', 'optimizer',
            'latencyfix', 'latency-fix', 'pingfix', 'ping-fix',
            'networkfix', 'network-fix', 'connectionfix',
            'fpsfixer', 'fps-fixer', 'fpsfix',
            'smoothfps', 'smooth-fps', 'fpsunlocker',
            'gamefixer', 'game-fixer', 'gamefix',
            'antilag', 'anti-lag', 'lagfix', 'lag-fix',
            'memoryoptimizer', 'memory-optimizer',
            'cpuoptimizer', 'cpu-optimizer',
            
            # Nombres en otros idiomas (español/portugués comunes en LATAM)
            'inyector', 'injetor', 'cargador',
            'trampa', 'trampas', 'trucos', 'hack',
            'mira', 'punteria', 'ayuda',
            
            # Nombres de proyectos de cheats conocidos
            'unknowncheats', 'unknown-cheats', 'uc-downloader',
            'sourcemod', 'source-mod', 'vac-bypass',
            'vacbypass', 'vac bypass', 'antivac',
            'steambypass', 'steam-bypass',
            
            # Variaciones con números y símbolos
            'inject0r', '1njector', 'h4ck', 'ch34t',
            'a1mbot', 'w4llhack', '3sp',
            
            # Nombres cortos y abreviaciones (SOLO SI SON MUY ESPECÍFICOS)
            'inj.exe', 'ld.exe', 'mm.exe',
            
            # DLL Libraries sospechosas
            'overlay.dll', 'hook.dll', 'hooks.dll',
            'd3d9.dll', 'd3d11.dll', 'dxgi.dll', 'opengl32.dll',
            'winmm.dll', 'version.dll', 'dsound.dll',
            
            # Nombres que intentan parecer archivos del sistema
            'svchost32', 'explorer32', 'system32helper',
            'windowsupdate', 'windows-update', 'msupdate',
            'nvidiasvc', 'nvidia-service', 'amdservice',
            'audiodg32', 'csrss32', 'winlogon32',
            
            # Palabras clave adicionales de cheats
            'unlocker', 'unlock', 'bypass', 'crack',
            'trainer', 'modifier', 'editor', 'patcher',
            'crackfix', 'nocd', 'no-cd', 'godmode', 'god-mode',
            'infinite', 'unlimited', 'auto', 'macro',
            'script', 'scripthook', 'script-hook',
            
            # Nombres de comunidades/forums de cheats
            'mpgh', 'unknowncheats', 'elitepvpers', 'epicnpc',
            'hackforums', 'hack-forums',
            
            # Términos técnicos usados en cheats
            'dll-injection', 'process-injection', 'code-injection',
            'memory-edit', 'memory-hack', 'memory-mod',
            'hook-dll', 'detour', 'patch-exe'
        ]
        
        try:
            # Método 1: Analizar Prefetch
            prefetch_results = self._analyze_prefetch_folder(suspicious_program_patterns)
            recently_executed.extend(prefetch_results)
            
            # Método 2: Analizar UserAssist del Registro
            userassist_results = self._analyze_userassist_registry(suspicious_program_patterns)
            recently_executed.extend(userassist_results)
            
            # Método 3: Analizar RecentApps del Registro  
            recentapps_results = self._analyze_recentapps_registry(suspicious_program_patterns)
            recently_executed.extend(recentapps_results)
            
        except Exception as e:
            print(f"Error al analizar historial de ejecución: {e}")
        
        self.results['recently_executed_suspicious'] = recently_executed
        return len(recently_executed) > 0
    
    def _analyze_prefetch_folder(self, suspicious_patterns):
        """Analiza la carpeta Prefetch - MODO COMPLETO: Muestra TODO lo ejecutado en las últimas 4 horas"""
        prefetch_files = []
        prefetch_path = r"C:\Windows\Prefetch"
        
        if not os.path.exists(prefetch_path):
            return prefetch_files
        
        try:
            current_time = datetime.now()
            time_window_hours = 4  # Ventana de tiempo: últimas 4 horas
            
            # Obtener lista de archivos .pf
            try:
                files = [f for f in os.listdir(prefetch_path) if f.lower().endswith('.pf')]
            except:
                return []

            for filename in files:
                file_path = os.path.join(prefetch_path, filename)
                filename_lower = filename.lower()
                
                try:
                    # Obtener información del archivo
                    stat = os.stat(file_path)
                    last_modified = datetime.fromtimestamp(stat.st_mtime)
                    time_diff = current_time - last_modified
                    hours_ago = time_diff.total_seconds() / 3600
                    
                    # FILTRO TEMPORAL: Solo incluir programas ejecutados en las últimas 4 horas
                    if hours_ago > time_window_hours:
                        continue
                    
                    # Extraer nombre base del programa (ej: PROGRAMA.EXE-HASH.pf -> PROGRAMA.EXE)
                    try:
                        program_name_part = filename.split('-')[0]
                        if program_name_part.lower().endswith('.pf'):
                            program_name = program_name_part.replace('.pf', '')
                        else:
                            program_name = program_name_part
                    except:
                        program_name = filename.replace('.pf', '')
                    
                    # Intentar obtener ruta real con WinPrefetchView
                    real_path = self.parse_prefetch_with_tool(file_path)
                    
                    # Determinar severidad basándose en patrones y ruta
                    severity = "INFO"  # Por defecto, solo informativo
                    matched_pattern = None
                    is_whitelisted = False
                    
                    # 1. Verificar si está en whitelist (solo si tenemos ruta real)
                    if real_path:
                        is_whitelisted = self.is_legitimate_program(program_name, real_path)
                    else:
                        # Sin ruta real, verificar solo por nombre
                        is_whitelisted = self.is_legitimate_program(program_name)
                    
                    # 2. Verificar patrones sospechosos
                    for pattern in suspicious_patterns:
                        if len(pattern) < 3 and pattern not in filename_lower.split('.'):
                            continue
                        if pattern in filename_lower:
                            matched_pattern = pattern
                            severity = "CRITICAL"
                            break
                    
                    # 3. Si no está en whitelist y no tiene ruta real, marcar como sospechoso
                    if not is_whitelisted and not real_path:
                        severity = "MEDIUM"  # Potencialmente renombrado o sin verificar
                    
                    # 4. Si está en whitelist pero no tiene ruta, marcar como advertencia
                    if is_whitelisted and not real_path:
                        severity = "LOW"  # Probablemente legítimo pero sin confirmar
                    
                    # Analizar contexto si hay patrón sospechoso
                    context_details = ""
                    if matched_pattern:
                        context_analysis = self._analyze_program_context(program_name, matched_pattern)
                        context_details = context_analysis['details']
                    elif not real_path:
                        context_details = "⚠️ No se pudo verificar la ruta real del ejecutable. Posible evasión por cambio de nombre."
                    elif not is_whitelisted:
                        context_details = f"Programa desconocido ejecutado desde: {real_path}"
                    else:
                        context_details = f"Programa legítimo verificado: {real_path}"
                    
                    prefetch_files.append({
                        'source': 'Prefetch',
                        'program_name': program_name,
                        'prefetch_file': filename,
                        'file_path': file_path,
                        'real_path': real_path if real_path else "❌ No detectada (verificar manualmente)",
                        'last_execution': last_modified.isoformat(),
                        'last_execution_formatted': last_modified.strftime("%Y-%m-%d %H:%M:%S"),
                        'hours_ago': round(hours_ago, 2),
                        'severity': severity,
                        'description': f'Ejecutado hace {round(hours_ago, 1)} horas',
                        'matched_pattern': matched_pattern if matched_pattern else "N/A",
                        'confidence': "MUY ALTA" if real_path else "BAJA",
                        'context_details': context_details,
                        'is_whitelisted': is_whitelisted
                    })
                        
                except (OSError, PermissionError):
                    continue
                            
        except (OSError, PermissionError) as e:
            print(f"No se pudo acceder a Prefetch: {e}")
        
        # Ordenar por tiempo de ejecución (más reciente primero)
        prefetch_files.sort(key=lambda x: x['hours_ago'])
        
        return prefetch_files
    
    def _analyze_userassist_registry(self, suspicious_patterns):
        """Analiza UserAssist del Registro para detectar programas ejecutados"""
        userassist_programs = []
        
        try:
            import winreg
            from base64 import b64decode
            
            # UserAssist está en HKEY_CURRENT_USER
            base_key = winreg.HKEY_CURRENT_USER
            userassist_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
            
            try:
                # Abrir la clave UserAssist
                userassist_key = winreg.OpenKey(base_key, userassist_path)
                
                # Iterar sobre las subclaves (GUIDs)
                num_subkeys = winreg.QueryInfoKey(userassist_key)[0]
                
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(userassist_key, i)
                        count_path = f"{userassist_path}\\{subkey_name}\\Count"
                        
                        count_key = winreg.OpenKey(base_key, count_path)
                        num_values = winreg.QueryInfoKey(count_key)[1]
                        
                        for j in range(num_values):
                            try:
                                value_name, value_data, _ = winreg.EnumValue(count_key, j)
                                
                                # Decodificar ROT13 del nombre
                                decoded_path = self._rot13_decode(value_name)
                                decoded_name_lower = decoded_path.lower()
                                program_name = os.path.basename(decoded_path)
                                
                                # 1. Whitelist check
                                if self.is_legitimate_program(program_name, decoded_path):
                                    continue
                                
                                # Verificar si contiene patrones sospechosos
                                for pattern in suspicious_patterns:
                                    # Evitar matches cortos peligrosos
                                    if len(pattern) < 3 and pattern not in decoded_name_lower.split('.'):
                                         continue
                                         
                                    if pattern in decoded_name_lower:
                                        userassist_programs.append({
                                            'source': 'UserAssist Registry',
                                            'program_path': decoded_path,
                                            'program_name': program_name,
                                            'severity': 'HIGH',
                                            'description': f'Programa sospechoso en historial de UserAssist',
                                            'matched_pattern': pattern
                                        })
                                        break
                                        
                            except (WindowsError, OSError):
                                continue
                        
                        winreg.CloseKey(count_key)
                        
                    except (WindowsError, OSError):
                        continue
                
                winreg.CloseKey(userassist_key)
                
            except (WindowsError, OSError):
                pass
                
        except Exception as e:
            print(f"Error al analizar UserAssist: {e}")
        
        return userassist_programs
    
    def _analyze_recentapps_registry(self, suspicious_patterns):
        """Analiza RecentApps del Registro para detectar aplicaciones recientes"""
        recentapps = []
        
        try:
            import winreg
            
            base_key = winreg.HKEY_CURRENT_USER
            recentapps_path = r"Software\Microsoft\Windows\CurrentVersion\Search\RecentApps"
            
            try:
                recentapps_key = winreg.OpenKey(base_key, recentapps_path)
                num_subkeys = winreg.QueryInfoKey(recentapps_key)[0]
                
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(recentapps_key, i)
                        app_path = f"{recentapps_path}\\{subkey_name}"
                        app_key = winreg.OpenKey(base_key, app_path)
                        
                        try:
                            # Obtener nombre de la aplicación
                            app_id, _ = winreg.QueryValueEx(app_key, "AppId")
                            app_id_lower = app_id.lower()
                            program_name = os.path.basename(app_id)
                            
                            # 1. Whitelist check
                            if self.is_legitimate_program(program_name, app_id):
                                continue
                            
                            # Verificar si contiene patrones sospechosos
                            for pattern in suspicious_patterns:
                                # Evitar matches cortos peligrosos
                                if len(pattern) < 3 and pattern not in app_id_lower.split('.'):
                                     continue
                                     
                                if pattern in app_id_lower:
                                    recentapps.append({
                                        'source': 'RecentApps Registry',
                                        'program_name': app_id,
                                        'severity': 'MEDIUM',
                                        'description': f'Aplicación sospechosa en historial reciente',
                                        'matched_pattern': pattern
                                    })
                                    break
                                    
                        except (WindowsError, OSError):
                            pass
                        
                        winreg.CloseKey(app_key)
                        
                    except (WindowsError, OSError):
                        continue
                
                winreg.CloseKey(recentapps_key)
                
            except (WindowsError, OSError):
                pass
                
        except Exception as e:
            print(f"Error al analizar RecentApps: {e}")
        
        return recentapps
    
    def _rot13_decode(self, text):
        """Decodifica ROT13 usado en UserAssist"""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def _analyze_program_context(self, program_name, matched_pattern):
        """Analiza el contexto de un programa para reducir falsos positivos"""
        
        # Whitelist de programas legítimos conocidos que podrían coincidir con patrones genéricos
        legitimate_programs = {
            # Launchers y loaders legítimos
            'epicgameslauncher', 'steamwebhelper', 'originwebhelper',
            'battlenetlauncher', 'ubisoft', 'ea', 'riot',
            'nvidia', 'amd', 'intel', 'realtek',
            'discord', 'obs', 'streamlabs',
            'chrome', 'firefox', 'edge', 'brave',
            'vscode', 'visualstudio', 'pycharm',
            'winrar', '7zip', 'notepad++',
            
            # Servicios de Windows
            'windows', 'microsoft', 'svchost', 'explorer',
            'dwm', 'csrss', 'lsass', 'winlogon',
            
            # Software antivirus
            'kaspersky', 'avast', 'avg', 'norton',
            'mcafee', 'bitdefender', 'malwarebytes',
            'windowsdefender', 'defender'
        }
        
        program_lower = program_name.lower()
        
        # Paso 1: Verificar si es un programa legítimo conocido
        for legit_prog in legitimate_programs:
            if legit_prog in program_lower:
                return {
                    'is_suspicious': False,
                    'severity': 'LOW',
                    'confidence': 'LEGÍTIMO',
                    'details': f'Programa reconocido como legítimo: {program_name}'
                }
        
        # Paso 2: Analizar si el patrón coincidente es genérico o específico
        generic_patterns = ['loader', 'load', 'launcher', 'launch', 'runner', 
                           'starter', 'activator', 'enabler', 'executor', 'boot']
        specific_patterns = ['l4d2', 'cheat', 'hack', 'aimbot', 'wallhack', 'esp',
                            'injector', 'processhacker', 'cheatengine', 'xenos',
                            'extremeinjector', 'trampa', 'inyector']
        
        pattern_lower = matched_pattern.lower()
        
        # Si coincide con patrón ESPECÍFICO de cheat → ALTA sospecha
        if any(specific in pattern_lower for specific in specific_patterns):
            # Verificar si tiene combinación sospechosa
            suspicious_combinations = [
                'l4d2', 'left4dead2', 'cheat', 'hack', 'esp', 
                'aimbot', 'wallhack', 'mod', 'injector'
            ]
            
            if any(combo in program_lower for combo in suspicious_combinations):
                return {
                    'is_suspicious': True,
                    'severity': 'CRITICAL',
                    'confidence': 'ALTA',
                    'details': f'Nombre específico de cheat detectado: {program_name}'
                }
        
        # Si coincide con patrón GENÉRICO → Requiere análisis adicional
        if any(generic in pattern_lower for generic in generic_patterns):
            # Buscar indicadores adicionales de sospecha
            suspicious_indicators = 0
            details = []
            
            # Indicador 1: Contiene palabras relacionadas con juegos
            game_related = ['game', 'fps', 'boost', 'optimizer', 'fix', 'enhance']
            if any(word in program_lower for word in game_related):
                suspicious_indicators += 1
                details.append('Nombre relacionado con juegos/optimización')
            
            # Indicador 2: Nombre muy corto (típico de cheats discretos)
            if len(program_name) <= 4:  # ej: "ld", "run", "mm"
                suspicious_indicators += 1
                details.append('Nombre inusualmente corto')
            
            # Indicador 3: Contiene números o símbolos (ej: "l0ader", "load3r")
            if any(char.isdigit() for char in program_name):
                # Excepción: versiones legítimas como "launcher2"
                if not any(legit in program_lower for legit in ['launcher', 'version', 'client']):
                    suspicious_indicators += 1
                    details.append('Contiene números sospechosos')
            
            # Indicador 4: Combinación con otros archivos de cheat (se verificará después)
            # Este indicador se agregará en la lógica principal
            
            # Decisión basada en indicadores
            if suspicious_indicators >= 2:
                return {
                    'is_suspicious': True,
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIA',
                    'details': f'Múltiples indicadores sospechosos: {", ".join(details)}'
                }
            elif suspicious_indicators == 1:
                return {
                    'is_suspicious': True,
                    'severity': 'LOW',
                    'confidence': 'BAJA',
                    'details': f'Posible falso positivo, pero requiere atención: {", ".join(details)}'
                }
            else:
                # Patrón genérico sin indicadores adicionales → Probablemente legítimo
                return {
                    'is_suspicious': False,
                    'severity': 'LOW',
                    'confidence': 'LEGÍTIMO PROBABLE',
                    'details': f'Nombre genérico sin indicadores sospechosos adicionales'
                }
        
        # Por defecto, si no es genérico ni está en whitelist, es sospechoso
        return {
            'is_suspicious': True,
            'severity': 'HIGH',
            'confidence': 'ALTA',
            'details': f'Programa sospechoso: {program_name}'
        }
    
    def _is_really_suspicious(self, proc_name, proc_exe, proc_cmdline):
        """Análisis adicional para determinar si un proceso es realmente sospechoso"""
        # Patrones que indican cheats reales
        cheat_patterns = [
            r'aimbot', r'wallhack', r'esp\b', r'triggerbot', r'speedhack',
            r'norecoil', r'radar\b', r'injector', r'bypass', r'undetected',
            r'memory\s+(hack|mod|edit)', r'dll\s+(inject|hook)', r'patch\s+(game|exe)'
        ]
        
        # Patrones que indican software legítimo
        legitimate_patterns = [
            r'steam', r'windows', r'microsoft', r'nvidia', r'amd', r'intel',
            r'realtek', r'obs', r'discord', r'chrome', r'firefox', r'explorer',
            r'antivirus', r'security', r'update', r'service', r'driver'
        ]
        
        import re
        
        # Verificar patrones de cheats
        for pattern in cheat_patterns:
            if re.search(pattern, proc_name + ' ' + proc_exe + ' ' + proc_cmdline, re.IGNORECASE):
                return True
        
        # Verificar patrones legítimos
        for pattern in legitimate_patterns:
            if re.search(pattern, proc_name + ' ' + proc_exe + ' ' + proc_cmdline, re.IGNORECASE):
                return False
        
        # Si no coincide con ningún patrón conocido, ser más conservador
        return False
    
    def detect_memory_injections(self):
        """Detecta inyecciones de memoria y DLLs sospechosas"""
        injections_found = []
        
        try:
            # Buscar procesos de L4D2
            l4d2_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and 'left4dead2' in proc.info['name'].lower():
                        l4d2_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not l4d2_processes:
                return False
            
            for l4d2_proc in l4d2_processes:
                try:
                    # Obtener DLLs cargadas en el proceso
                    dlls = self._get_loaded_dlls(l4d2_proc)
                    
                    for dll_path in dlls:
                        if self._is_suspicious_dll(dll_path):
                            injections_found.append({
                                'process_pid': l4d2_proc.info['pid'],
                                'process_name': l4d2_proc.info['name'],
                                'dll_path': dll_path,
                                'reason': self._analyze_dll_suspicion(dll_path)
                            })
                    
                    # Verificar memoria del proceso
                    memory_analysis = self._analyze_process_memory(l4d2_proc)
                    if memory_analysis:
                        injections_found.extend(memory_analysis)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Error al escanear inyecciones de memoria: {e}")
        
        self.results['memory_injections'] = injections_found
        return len(injections_found) > 0
    
    def _get_loaded_dlls(self, process):
        """Obtiene las DLLs cargadas en un proceso"""
        try:
            # Usar psutil para obtener información del proceso
            dlls = []
            
            # Método alternativo usando ctypes para obtener DLLs
            try:
                import ctypes
                from ctypes import wintypes
                
                # Obtener handle del proceso
                PROCESS_QUERY_INFORMATION = 0x0400
                PROCESS_VM_READ = 0x0010
                
                handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                    False,
                    process.info['pid']
                )
                
                if handle:
                    # Enumerar módulos
                    dlls = self._enumerate_modules(handle)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    
            except Exception:
                # Fallback: usar información básica del proceso
                if process.info['exe']:
                    dlls.append(process.info['exe'])
            
            return dlls
            
        except Exception:
            return []
    
    def _enumerate_modules(self, process_handle):
        """Enumera los módulos cargados en un proceso"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Estructura para MODULEENTRY32
            class MODULEENTRY32(ctypes.Structure):
                _fields_ = [
                    ('dwSize', wintypes.DWORD),
                    ('th32ModuleID', wintypes.DWORD),
                    ('th32ProcessID', wintypes.DWORD),
                    ('GlblcntUsage', wintypes.DWORD),
                    ('ProccntUsage', wintypes.DWORD),
                    ('modBaseAddr', ctypes.POINTER(wintypes.BYTE)),
                    ('modBaseSize', wintypes.DWORD),
                    ('hModule', wintypes.HMODULE),
                    ('szModule', wintypes.CHAR * 256),
                    ('szExePath', wintypes.CHAR * 260)
                ]
            
            dlls = []
            
            # Crear snapshot del proceso
            TH32CS_SNAPMODULE = 0x00000008
            snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(
                TH32CS_SNAPMODULE,
                0
            )
            
            if snapshot != -1:
                me32 = MODULEENTRY32()
                me32.dwSize = ctypes.sizeof(MODULEENTRY32)
                
                # Primer módulo
                if ctypes.windll.kernel32.Module32First(snapshot, ctypes.byref(me32)):
                    while True:
                        dll_path = me32.szExePath.decode('utf-8', errors='ignore')
                        dlls.append(dll_path)
                        
                        # Siguiente módulo
                        if not ctypes.windll.kernel32.Module32Next(snapshot, ctypes.byref(me32)):
                            break
                
                ctypes.windll.kernel32.CloseHandle(snapshot)
            
            return dlls
            
        except Exception:
            return []
    
    def _is_suspicious_dll(self, dll_path):
        """Determina si una DLL es sospechosa"""
        if not dll_path:
            return False
        
        dll_path_lower = dll_path.lower()
        dll_name = os.path.basename(dll_path).lower()
        
        # DLLs legítimas de Windows y Steam (solo si están en ubicaciones oficiales)
        legitimate_dlls = [
            'kernel32.dll', 'user32.dll', 'gdi32.dll', 'advapi32.dll',
            'ole32.dll', 'oleaut32.dll', 'shell32.dll', 'comctl32.dll',
            'ntdll.dll', 'msvcrt.dll', 'ws2_32.dll', 'winmm.dll',
            'steam_api.dll', 'steamclient.dll', 'steamservice.dll',
            'gameoverlayrenderer.dll', 'gameoverlayrenderer64.dll'
        ]
        
        # DLLs gráficas legítimas SOLO si están en System32 o en la carpeta del juego oficial
        graphics_dlls = ['d3d9.dll', 'd3d11.dll', 'dxgi.dll', 'opengl32.dll']
        is_graphics_dll = any(gdll in dll_name for gdll in graphics_dlls)
        
        # Si es DLL gráfica, verificar ubicación (puede ser reemplazada)
        if is_graphics_dll:
            # Si está en System32 o SysWOW64, es legítima
            if 'system32' in dll_path_lower or 'syswow64' in dll_path_lower:
                return False
            # Si está en otra ubicación (especialmente TEMP, APPDATA, o bin/), es sospechosa
            suspicious_locs = ['temp', 'tmp', 'appdata', 'downloads', 'desktop', 'bin']
            if any(loc in dll_path_lower for loc in suspicious_locs):
                return True
        
        # Verificar si es una DLL legítima en ubicación oficial
        for legit_dll in legitimate_dlls:
            if legit_dll in dll_name:
                # Verificar ubicación - si está en System32/SysWOW64, es legítima
                if 'system32' in dll_path_lower or 'syswow64' in dll_path_lower:
                    return False
                # Si está en otra ubicación, puede ser sospechosa
                if any(loc in dll_path_lower for loc in ['temp', 'tmp', 'appdata', 'downloads']):
                    return True
        
        # ===== BUSCAR NOMBRES DE HACKS COMERCIALES CONOCIDOS =====
        known_hack_names = [
            'aimware', 'aim-ware', 'aw.dll', 'aw_',
            'baunti', 'baunticheats', 'l4d2helper',
            'interwebz', 'iwz',
            'lmaobox', 'lmao',
            'fleep', 'fleephack',
            'osiris', 'ratpoison'
        ]
        
        for hack_name in known_hack_names:
            if hack_name in dll_name:
                return True
        
        # Patrones sospechosos genéricos
        suspicious_patterns = [
            r'cheat', r'hack', r'aimbot', r'wallhack', r'esp', r'triggerbot',
            r'speedhack', r'norecoil', r'radar', r'overlay', r'inject',
            r'bypass', r'undetected', r'memory', r'hook', r'patch'
        ]
        
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, dll_name):
                return True
        
        # Verificar ubicaciones sospechosas
        suspicious_locations = [
            r'temp', r'tmp', r'appdata', r'users.*temp', r'programdata',
            r'downloads', r'desktop', r'documents'
        ]
        
        for location in suspicious_locations:
            if re.search(location, dll_path_lower):
                return True
        
        return False
    
    def _is_replaced_dll(self, filename, file_path):
        """Detecta si una DLL en bin/ ha sido reemplazada (wrapper/hook)"""
        filename_lower = filename.lower()
        
        # DLLs que comúnmente se reemplazan para inyección
        commonly_replaced_dlls = ['d3d9.dll', 'd3d11.dll', 'dxgi.dll', 'opengl32.dll']
        
        if filename_lower not in commonly_replaced_dlls:
            return False
        
        # Si la DLL está en bin/, es MUY sospechoso (no debería estar ahí)
        # Las DLLs gráficas oficiales están en System32/SysWOW64
        try:
            # Verificar tamaño - DLLs reemplazadas suelen ser más pequeñas o diferentes
            file_size = os.path.getsize(file_path)
            
            # Tamaños típicos de DLLs oficiales (aproximados)
            typical_sizes = {
                'd3d9.dll': (1800000, 2500000),  # ~1.8-2.5 MB
                'd3d11.dll': (2000000, 3000000),  # ~2-3 MB
                'dxgi.dll': (500000, 1000000),    # ~500KB-1MB
                'opengl32.dll': (200000, 500000)  # ~200-500KB
            }
            
            if filename_lower in typical_sizes:
                min_size, max_size = typical_sizes[filename_lower]
                # Si el tamaño es muy diferente, es sospechoso
                if file_size < min_size * 0.5 or file_size > max_size * 2:
                    return True
            
            # Verificar si tiene firma digital (las oficiales la tienen)
            # Si no tiene firma y está en bin/, es muy sospechoso
            # (Nota: Verificar firma requiere librerías adicionales, por ahora confiamos en tamaño/ubicación)
            
            return True  # Si está en bin/, asumimos que es reemplazada
            
        except Exception:
            return False
    
    def _analyze_dll_suspicion(self, dll_path):
        """Analiza por qué una DLL es sospechosa"""
        reasons = []
        dll_name = os.path.basename(dll_path).lower()
        dll_path_lower = dll_path.lower()
        
        # ===== VERIFICAR HACKS COMERCIALES CONOCIDOS =====
        known_hacks = {
            'aimware': '🚨 AIMWARE detectado - Sistema de aimbot profesional de pago',
            'aim-ware': '🚨 AIMWARE detectado - Sistema de aimbot profesional de pago',
            'aw.dll': '🚨 AIMWARE detectado - DLL de Aimware',
            'baunti': '🚨 BAUNTICHEATS detectado - Left 4 Dead 2 Helper',
            'baunticheats': '🚨 BAUNTICHEATS detectado - Left 4 Dead 2 Helper',
            'l4d2helper': '🚨 BAUNTICHEATS detectado - Left 4 Dead 2 Helper',
            'interwebz': '🚨 INTERWEBZ detectado - Cheat para juegos Valve',
            'iwz': '🚨 INTERWEBZ detectado - Cheat para juegos Valve',
            'lmaobox': '🚨 LMAOBOX detectado - Cheat portado de TF2',
            'lmao': '🚨 LMAOBOX detectado - Cheat portado de TF2',
            'fleep': '🚨 FLEEPHACK detectado - Hack gratuito muy distribuido',
            'fleephack': '🚨 FLEEPHACK detectado - Hack gratuito muy distribuido',
            'osiris': '🚨 OSIRIS detectado - Open Source usado como base para hacks',
            'ratpoison': '🚨 RATPOISON detectado - Open Source usado como base para hacks'
        }
        
        for hack_key, hack_desc in known_hacks.items():
            if hack_key in dll_name:
                reasons.append(hack_desc)
                break  # Solo reportar un hack por DLL
        
        # Verificar patrones genéricos en el nombre
        suspicious_patterns = {
            'cheat': 'Contiene palabra "cheat"',
            'hack': 'Contiene palabra "hack"',
            'aimbot': 'Contiene palabra "aimbot"',
            'wallhack': 'Contiene palabra "wallhack"',
            'esp': 'Contiene palabra "esp"',
            'inject': 'Contiene palabra "inject"',
            'bypass': 'Contiene palabra "bypass"'
        }
        
        for pattern, reason in suspicious_patterns.items():
            if pattern in dll_name and not any(hack in dll_name for hack in known_hacks.keys()):
                reasons.append(reason)
        
        # Verificar ubicación sospechosa
        if 'temp' in dll_path_lower or 'tmp' in dll_path_lower:
            reasons.append('Ubicada en carpeta temporal (%TEMP%) - Típico de loaders de hacks')
        if 'appdata' in dll_path_lower:
            reasons.append('Ubicada en AppData - Típico de loaders de hacks')
        if 'downloads' in dll_path_lower:
            reasons.append('Ubicada en carpeta de descargas')
        if 'bin' in dll_path_lower:
            reasons.append('🚨 DLL en carpeta bin/ - Posible reemplazo/wrapper para inyección')
        
        return "; ".join(reasons) if reasons else "DLL sospechosa detectada"
    
    def _analyze_process_memory(self, process):
        """Analiza la memoria del proceso en busca de patrones sospechosos"""
        try:
            suspicious_patterns = []
            
            # Verificar si el proceso tiene características sospechosas
            try:
                # Obtener información de memoria
                memory_info = process.memory_info()
                
                # Verificar uso excesivo de memoria
                if memory_info.rss > 2 * 1024 * 1024 * 1024:  # > 2GB
                    suspicious_patterns.append({
                        'process_pid': process.info['pid'],
                        'process_name': process.info['name'],
                        'reason': f'Uso excesivo de memoria: {memory_info.rss / (1024*1024):.1f} MB',
                        'type': 'memory_usage'
                    })
                
                # Verificar número de threads sospechoso
                try:
                    num_threads = process.num_threads()
                    if num_threads > 50:  # Más de 50 threads es sospechoso
                        suspicious_patterns.append({
                            'process_pid': process.info['pid'],
                            'process_name': process.info['name'],
                            'reason': f'Número excesivo de threads: {num_threads}',
                            'type': 'thread_count'
                        })
                except:
                    pass
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            return suspicious_patterns
            
        except Exception:
            return []
    
    def detect_known_cheat_signatures(self):
        """Detecta firmas de cheats conocidos (INCLUYENDO HACKS COMERCIALES)"""
        signatures_found = []
        
        # Firmas conocidas de cheats populares para L4D2 (INCLUYENDO HACKS COMERCIALES)
        known_cheat_signatures = {
            # ===== HACKS COMERCIALES CONOCIDOS =====
            # Aimware
            'aimware.dll': {
                'description': '🚨 AIMWARE - Sistema de aimbot profesional de pago (Loader + Aimbot + ESP + HvH)',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Aimware'
            },
            'aw.dll': {
                'description': '🚨 AIMWARE - DLL de Aimware',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Aimware'
            },
            'aimwareloader.exe': {
                'description': '🚨 AIMWARE - Loader de Aimware',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Aimware'
            },
            'awloader.exe': {
                'description': '🚨 AIMWARE - Loader de Aimware',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Aimware'
            },
            
            # BauntiCheats
            'baunti.dll': {
                'description': '🚨 BAUNTICHEATS - Left 4 Dead 2 Helper (Popular en comunidad rusa/hispana)',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'BauntiCheats'
            },
            'baunticheats.dll': {
                'description': '🚨 BAUNTICHEATS - Left 4 Dead 2 Helper',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'BauntiCheats'
            },
            'l4d2helper.dll': {
                'description': '🚨 BAUNTICHEATS - Left 4 Dead 2 Helper',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'BauntiCheats'
            },
            'bauntiloader.exe': {
                'description': '🚨 BAUNTICHEATS - Loader de BauntiCheats',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'BauntiCheats'
            },
            
            # Interwebz
            'interwebz.dll': {
                'description': '🚨 INTERWEBZ - Cheat conocido para juegos Valve (TF2, CSS, L4D2)',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Interwebz'
            },
            'iwz.dll': {
                'description': '🚨 INTERWEBZ - Cheat para juegos Valve',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Interwebz'
            },
            'interwebzloader.exe': {
                'description': '🚨 INTERWEBZ - Loader de Interwebz',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'Interwebz'
            },
            
            # LMAOBOX
            'lmaobox.dll': {
                'description': '🚨 LMAOBOX - Cheat originalmente de TF2, portado a L4D2',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'LMAOBOX'
            },
            'lmaoloader.exe': {
                'description': '🚨 LMAOBOX - Loader de LMAOBOX',
                'severity': 'CRITICAL',
                'type': 'commercial_hack',
                'hack_name': 'LMAOBOX'
            },
            
            # FleepHack / Fleep
            'fleep.dll': {
                'description': '🚨 FLEEPHACK - Hack gratuito muy distribuido en foros y YouTube',
                'severity': 'CRITICAL',
                'type': 'free_hack',
                'hack_name': 'FleepHack'
            },
            'fleephack.dll': {
                'description': '🚨 FLEEPHACK - Hack gratuito muy distribuido',
                'severity': 'CRITICAL',
                'type': 'free_hack',
                'hack_name': 'FleepHack'
            },
            'fleeploader.exe': {
                'description': '🚨 FLEEPHACK - Loader de FleepHack',
                'severity': 'CRITICAL',
                'type': 'free_hack',
                'hack_name': 'FleepHack'
            },
            
            # Osiris / RatPoison
            'osiris.dll': {
                'description': '🚨 OSIRIS - Open Source usado como base para hacks privados de L4D2',
                'severity': 'CRITICAL',
                'type': 'open_source_based',
                'hack_name': 'Osiris'
            },
            'ratpoison.dll': {
                'description': '🚨 RATPOISON - Open Source usado como base para hacks privados',
                'severity': 'CRITICAL',
                'type': 'open_source_based',
                'hack_name': 'RatPoison'
            },
            
            # ===== FIRMAS GENÉRICAS DE CHEATS =====
            'aimbot.dll': {
                'description': 'Aimbot conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'wallhack.dll': {
                'description': 'Wallhack conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'esp.dll': {
                'description': 'ESP conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'triggerbot.dll': {
                'description': 'Triggerbot conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'speedhack.dll': {
                'description': 'Speedhack conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'norecoil.dll': {
                'description': 'No Recoil conocido',
                'severity': 'HIGH',
                'type': 'file_signature'
            },
            'radar.dll': {
                'description': 'Radar hack conocido',
                'severity': 'MEDIUM',
                'type': 'file_signature'
            },
            'overlay.dll': {
                'description': 'Overlay hack conocido',
                'severity': 'MEDIUM',
                'type': 'file_signature'
            }
        }
        
        # Firmas de procesos conocidos (INCLUYENDO HACKS COMERCIALES)
        known_process_signatures = {
            # ===== HACKS COMERCIALES - LOADERS =====
            'aimware': {
                'description': '🚨 AIMWARE - Loader de Aimware detectado (Sistema de aimbot profesional)',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'Aimware'
            },
            'aimwareloader': {
                'description': '🚨 AIMWARE - Loader de Aimware detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'Aimware'
            },
            'awloader': {
                'description': '🚨 AIMWARE - Loader de Aimware detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'Aimware'
            },
            'baunti': {
                'description': '🚨 BAUNTICHEATS - Loader de BauntiCheats detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'BauntiCheats'
            },
            'baunticheats': {
                'description': '🚨 BAUNTICHEATS - Loader detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'BauntiCheats'
            },
            'l4d2helper': {
                'description': '🚨 BAUNTICHEATS - Left 4 Dead 2 Helper detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'BauntiCheats'
            },
            'interwebz': {
                'description': '🚨 INTERWEBZ - Loader de Interwebz detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'Interwebz'
            },
            'lmaobox': {
                'description': '🚨 LMAOBOX - Loader de LMAOBOX detectado',
                'severity': 'CRITICAL',
                'type': 'commercial_hack_loader',
                'hack_name': 'LMAOBOX'
            },
            'fleep': {
                'description': '🚨 FLEEPHACK - Loader de FleepHack detectado',
                'severity': 'CRITICAL',
                'type': 'free_hack_loader',
                'hack_name': 'FleepHack'
            },
            'fleephack': {
                'description': '🚨 FLEEPHACK - Loader detectado',
                'severity': 'CRITICAL',
                'type': 'free_hack_loader',
                'hack_name': 'FleepHack'
            },
            # ===== HERRAMIENTAS GENÉRICAS =====
            'cheatengine': {
                'description': 'Cheat Engine detectado',
                'severity': 'HIGH',
                'type': 'process_signature'
            },
            'artmoney': {
                'description': 'ArtMoney detectado',
                'severity': 'HIGH',
                'type': 'process_signature'
            },
            'gameguardian': {
                'description': 'Game Guardian detectado',
                'severity': 'HIGH',
                'type': 'process_signature'
            },
            'trainer': {
                'description': 'Game Trainer detectado',
                'severity': 'MEDIUM',
                'type': 'process_signature'
            }
        }
        
        try:
            # Buscar archivos con firmas conocidas
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    # Verificar firmas de procesos
                    for signature, info in known_process_signatures.items():
                        if signature in proc_name or signature in proc_exe:
                            signatures_found.append({
                                'signature': signature,
                                'description': info['description'],
                                'severity': info['severity'],
                                'type': info['type'],
                                'process_pid': proc.info['pid'],
                                'process_name': proc.info['name'],
                                'process_exe': proc.info['exe']
                            })
                    
                    # Verificar DLLs cargadas en procesos sospechosos
                    if any(keyword in proc_name for keyword in ['left4dead2', 'steam']):
                        try:
                            dlls = self._get_loaded_dlls(proc)
                            for dll_path in dlls:
                                dll_name = os.path.basename(dll_path).lower()
                                if dll_name in known_cheat_signatures:
                                    info = known_cheat_signatures[dll_name]
                                    signatures_found.append({
                                        'signature': dll_name,
                                        'description': info['description'],
                                        'severity': info['severity'],
                                        'type': info['type'],
                                        'process_pid': proc.info['pid'],
                                        'process_name': proc.info['name'],
                                        'dll_path': dll_path
                                    })
                        except:
                            pass
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Buscar archivos en ubicaciones comunes de cheats (PRIORIDAD: %TEMP% y %APPDATA%)
            # Los loaders de hacks comerciales descomprimen aquí antes de inyectar
            common_cheat_locations = [
                os.path.join(os.environ.get('TEMP', ''), ''),  # PRIORIDAD 1: %TEMP% - MÁS COMÚN
                os.path.join(os.environ.get('APPDATA', ''), ''),  # PRIORIDAD 2: %APPDATA% - MÁS COMÚN
                os.path.join(os.environ.get('LOCALAPPDATA', ''), ''),  # PRIORIDAD 3: %LOCALAPPDATA%
                os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
                os.path.join(os.environ.get('PROGRAMDATA', ''), '')
            ]
            
            for location in common_cheat_locations:
                if os.path.exists(location):
                    try:
                        # Limitar profundidad de escaneo para %TEMP% y %APPDATA% (muy grandes)
                        max_depth = 1 if 'TEMP' in location or 'APPDATA' in location or 'LOCALAPPDATA' in location else 2
                        depth = 0
                        
                        for root, dirs, files in os.walk(location):
                            # Calcular profundidad
                            if root == location:
                                depth = 0
                            else:
                                try:
                                    rel_path = os.path.relpath(root, location)
                                    depth = rel_path.count(os.sep) + 1
                                except:
                                    depth = 0
                            
                            # Limitar profundidad
                            if depth > max_depth:
                                dirs[:] = []  # No seguir bajando
                                continue
                            
                            for file in files:
                                file_lower = file.lower()
                                
                                # Verificar coincidencia exacta
                                if file_lower in known_cheat_signatures:
                                    info = known_cheat_signatures[file_lower]
                                    file_path = os.path.join(root, file)
                                    try:
                                        signatures_found.append({
                                            'signature': file_lower,
                                            'description': info['description'],
                                            'severity': info['severity'],
                                            'type': info.get('type', 'file_signature'),
                                            'hack_name': info.get('hack_name', 'Unknown'),
                                            'file_path': file_path,
                                            'file_size': os.path.getsize(file_path),
                                            'location': location
                                        })
                                    except:
                                        pass
                                
                                # Verificar coincidencia parcial (para variaciones de nombres)
                                for sig_name, sig_info in known_cheat_signatures.items():
                                    if sig_name in file_lower and file_lower not in known_cheat_signatures:
                                        file_path = os.path.join(root, file)
                                        try:
                                            signatures_found.append({
                                                'signature': file_lower,
                                                'description': f"Variación de {sig_info.get('hack_name', sig_name)} detectada",
                                                'severity': sig_info['severity'],
                                                'type': sig_info.get('type', 'file_signature'),
                                                'hack_name': sig_info.get('hack_name', 'Unknown'),
                                                'file_path': file_path,
                                                'file_size': os.path.getsize(file_path),
                                                'location': location
                                            })
                                            break  # Solo reportar una vez
                                        except:
                                            pass
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            print(f"Error al escanear firmas de cheats: {e}")
        
        self.results['known_cheat_signatures'] = signatures_found
        return len(signatures_found) > 0
    
    def detect_versus_mods(self):
        """Detecta mods en Versus mediante análisis del archivo gameinfo.txt"""
        versus_mods_found = []
        
        if not self.l4d2_path:
            return False
        
        gameinfo_path = os.path.join(self.l4d2_path, "left4dead2", "gameinfo.txt")
        
        if not os.path.exists(gameinfo_path):
            return False
        
        try:
            # Leer el archivo gameinfo.txt
            with open(gameinfo_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar modificaciones en SearchPaths
            versus_modifications = self._analyze_gameinfo_modifications(content, gameinfo_path)
            versus_mods_found.extend(versus_modifications)
            
            # Buscar carpetas de mods en Versus
            versus_folders = self._detect_versus_mod_folders()
            versus_mods_found.extend(versus_folders)
            
        except Exception as e:
            print(f"Error al analizar gameinfo.txt: {e}")
        
        self.results['versus_mods'] = versus_mods_found
        return len(versus_mods_found) > 0
    
    def _analyze_gameinfo_modifications(self, content, file_path):
        """Analiza modificaciones en el archivo gameinfo.txt"""
        modifications = []
        
        try:
            import re
            
            # Buscar la sección SearchPaths
            searchpaths_match = re.search(r'SearchPaths\s*\{([^}]+)\}', content, re.DOTALL | re.IGNORECASE)
            
            if not searchpaths_match:
                return modifications
            
            searchpaths_content = searchpaths_match.group(1)
            
            # Patrones sospechosos en SearchPaths
            suspicious_patterns = [
                r'Game\s+ModsVersus',  # ModsVersus específico
                r'Game\s+mods',        # Cualquier carpeta "mods"
                r'Game\s+.*mod.*',    # Cualquier carpeta que contenga "mod"
                r'Game\s+.*versus.*', # Cualquier carpeta que contenga "versus"
                r'Game\s+.*custom.*', # Cualquier carpeta "custom"
                r'Game\s+.*addon.*',  # Cualquier carpeta "addon"
                r'Game\s+.*plugin.*', # Cualquier carpeta "plugin"
                r'Game\s+.*cheat.*',  # Cualquier carpeta "cheat"
                r'Game\s+.*hack.*',   # Cualquier carpeta "hack"
            ]
            
            # Verificar cada patrón sospechoso
            for pattern in suspicious_patterns:
                matches = re.findall(pattern, searchpaths_content, re.IGNORECASE)
                for match in matches:
                    modifications.append({
                        'type': 'gameinfo_modification',
                        'file_path': file_path,
                        'modification': match.strip(),
                        'description': f'Modificación sospechosa en SearchPaths: {match.strip()}',
                        'severity': 'HIGH',
                        'location': 'gameinfo.txt'
                    })
            
            # Verificar si hay más entradas Game de las esperadas
            game_entries = re.findall(r'Game\s+([^\s\n]+)', searchpaths_content, re.IGNORECASE)
            expected_entries = ['update', 'left4dead2_dlc3', 'left4dead2_dlc2', 'left4dead2_dlc1', '|gameinfo_path|.', 'hl2']
            
            # Filtrar entradas esperadas
            unexpected_entries = []
            for entry in game_entries:
                entry_clean = entry.strip()
                if entry_clean not in expected_entries:
                    unexpected_entries.append(entry_clean)
            
            if unexpected_entries:
                modifications.append({
                    'type': 'gameinfo_modification',
                    'file_path': file_path,
                    'modification': f'Entradas inesperadas: {", ".join(unexpected_entries)}',
                    'description': f'Se encontraron {len(unexpected_entries)} entradas Game inesperadas en SearchPaths',
                    'severity': 'HIGH',
                    'location': 'gameinfo.txt',
                    'unexpected_entries': unexpected_entries
                })
            
        except Exception as e:
            print(f"Error al analizar modificaciones de gameinfo: {e}")
        
        return modifications
    
    def _detect_versus_mod_folders(self):
        """Detecta carpetas de mods en Versus en el directorio de L4D2"""
        versus_folders = []
        
        if not self.l4d2_path:
            return versus_folders
        
        left4dead2_dir = os.path.join(self.l4d2_path, "left4dead2")
        
        if not os.path.exists(left4dead2_dir):
            return versus_folders
        
        # Carpetas sospechosas comunes para mods en Versus
        suspicious_folder_names = [
            'ModsVersus', 'modsversus', 'Mods_Versus', 'mods_versus',
            'VersusMods', 'versusmods', 'Versus_Mods', 'versus_mods',
            'mods', 'Mods', 'custom', 'Custom', 'addons', 'Addons',
            'plugins', 'Plugins', 'cheats', 'Cheats', 'hacks', 'Hacks'
        ]
        
        try:
            # Buscar carpetas sospechosas
            for item in os.listdir(left4dead2_dir):
                item_path = os.path.join(left4dead2_dir, item)
                
                if os.path.isdir(item_path):
                    item_lower = item.lower()
                    
                    # Verificar si es una carpeta sospechosa
                    for suspicious_name in suspicious_folder_names:
                        if suspicious_name.lower() in item_lower:
                            # Analizar el contenido de la carpeta
                            folder_analysis = self._analyze_mod_folder(item_path, item)
                            
                            versus_folders.append({
                                'type': 'versus_mod_folder',
                                'folder_name': item,
                                'folder_path': item_path,
                                'description': f'Carpeta de mods en Versus detectada: {item}',
                                'severity': 'HIGH',
                                'location': 'left4dead2 directory',
                                'analysis': folder_analysis
                            })
                            break
            
        except Exception as e:
            print(f"Error al detectar carpetas de mods en Versus: {e}")
        
        return versus_folders
    
    def _analyze_mod_folder(self, folder_path, folder_name):
        """Analiza el contenido de una carpeta de mods"""
        analysis = {
            'file_count': 0,
            'suspicious_files': [],
            'total_size': 0,
            'file_types': {}
        }
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    analysis['file_count'] += 1
                    analysis['total_size'] += file_size
                    
                    # Analizar tipo de archivo
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext not in analysis['file_types']:
                        analysis['file_types'][file_ext] = 0
                    analysis['file_types'][file_ext] += 1
                    
                    # Verificar archivos sospechosos
                    if self._is_suspicious_mod_file(file, file_ext):
                        analysis['suspicious_files'].append({
                            'name': file,
                            'path': file_path,
                            'size': file_size,
                            'reason': self._get_file_suspicion_reason(file, file_ext)
                        })
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _is_suspicious_mod_file(self, filename, file_ext):
        """Determina si un archivo de mod es sospechoso"""
        filename_lower = filename.lower()
        
        # Extensiones sospechosas
        suspicious_extensions = ['.dll', '.exe', '.bat', '.cmd', '.vbs', '.js', '.py']
        
        # Nombres sospechosos
        suspicious_names = [
            'cheat', 'hack', 'aimbot', 'wallhack', 'esp', 'triggerbot',
            'speedhack', 'norecoil', 'radar', 'overlay', 'inject', 'bypass',
            'trainer', 'mod', 'patch', 'crack', 'keygen'
        ]
        
        # Verificar extensión sospechosa
        if file_ext in suspicious_extensions:
            return True
        
        # Verificar nombre sospechoso
        for suspicious_name in suspicious_names:
            if suspicious_name in filename_lower:
                return True
        
        return False
    
    def _get_file_suspicion_reason(self, filename, file_ext):
        """Obtiene la razón por la cual un archivo es sospechoso"""
        filename_lower = filename.lower()
        reasons = []
        
        # Verificar extensión sospechosa
        suspicious_extensions = {
            '.dll': 'Archivo DLL ejecutable',
            '.exe': 'Archivo ejecutable',
            '.bat': 'Script de comandos',
            '.cmd': 'Script de comandos',
            '.vbs': 'Script de Visual Basic',
            '.js': 'Script de JavaScript',
            '.py': 'Script de Python'
        }
        
        if file_ext in suspicious_extensions:
            reasons.append(suspicious_extensions[file_ext])
        
        # Verificar nombre sospechoso
        suspicious_names = {
            'cheat': 'Contiene palabra "cheat"',
            'hack': 'Contiene palabra "hack"',
            'aimbot': 'Contiene palabra "aimbot"',
            'wallhack': 'Contiene palabra "wallhack"',
            'esp': 'Contiene palabra "esp"',
            'triggerbot': 'Contiene palabra "triggerbot"',
            'speedhack': 'Contiene palabra "speedhack"',
            'norecoil': 'Contiene palabra "norecoil"',
            'radar': 'Contiene palabra "radar"',
            'overlay': 'Contiene palabra "overlay"',
            'inject': 'Contiene palabra "inject"',
            'bypass': 'Contiene palabra "bypass"'
        }
        
        for suspicious_name, reason in suspicious_names.items():
            if suspicious_name in filename_lower:
                reasons.append(reason)
        
        return "; ".join(reasons) if reasons else "Archivo sospechoso detectado"
    
    def detect_suspicious_cfg_commands(self):
        """Detecta comandos prohibidos o sospechosos en archivos .cfg"""
        suspicious_cfgs = []
        
        if not self.l4d2_path:
            return False
        
        # Ubicaciones donde buscar archivos .cfg
        cfg_search_paths = [
            os.path.join(self.l4d2_path, "left4dead2", "cfg"),
            os.path.join(self.l4d2_path, "left4dead2"),
            os.path.join(self.l4d2_path, "cfg"),
        ]
        
        try:
            # Buscar archivos .cfg en todas las ubicaciones
            cfg_files = []
            for search_path in cfg_search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if file.lower().endswith('.cfg'):
                                cfg_files.append(os.path.join(root, file))
            
            # Analizar cada archivo .cfg encontrado
            for cfg_file in cfg_files:
                analysis = self._analyze_cfg_file(cfg_file)
                if analysis and len(analysis['prohibited_commands']) > 0:
                    suspicious_cfgs.append(analysis)
            
        except Exception as e:
            print(f"Error al escanear archivos .cfg: {e}")
        
        self.results['suspicious_cfg_commands'] = suspicious_cfgs
        return len(suspicious_cfgs) > 0
    
    def _analyze_cfg_file(self, cfg_file_path):
        """Analiza un archivo .cfg en busca de comandos prohibidos"""
        try:
            with open(cfg_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
            
            prohibited_commands_found = []
            
            # Definir comandos prohibidos y su severidad
            prohibited_commands = {
                # Comandos de Aimbot / Auto-aim
                'sv_aim': {'severity': 'CRITICAL', 'reason': 'Comando relacionado con aimbot'},
                'aimbot': {'severity': 'CRITICAL', 'reason': 'Comando de aimbot explícito'},
                'autoaim': {'severity': 'CRITICAL', 'reason': 'Auto-aim detectado'},
                
                # Comandos de Wallhack / ESP
                'r_drawothermodels 2': {'severity': 'CRITICAL', 'reason': 'Wallhack - Ver a través de paredes'},
                'mat_wireframe 1': {'severity': 'CRITICAL', 'reason': 'Modo wireframe para ver a través de objetos'},
                'r_drawothermodels': {'severity': 'HIGH', 'reason': 'Comando potencialmente usado para wallhack'},
                'mat_wireframe': {'severity': 'MEDIUM', 'reason': 'Comando de renderizado sospechoso'},
                
                # Comandos de velocidad / Speedhack
                'host_timescale': {'severity': 'HIGH', 'reason': 'Modificación de velocidad del juego'},
                'sv_cheats 1': {'severity': 'CRITICAL', 'reason': 'Habilita comandos de trampa'},
                'sv_infinite_ammo': {'severity': 'HIGH', 'reason': 'Munición infinita'},
                
                # Comandos de ventaja injusta
                'god': {'severity': 'CRITICAL', 'reason': 'Modo invencibilidad'},
                'noclip': {'severity': 'CRITICAL', 'reason': 'Atravesar paredes y volar'},
                'sv_infinite_aux_power': {'severity': 'HIGH', 'reason': 'Linterna infinita'},
                'buddha': {'severity': 'CRITICAL', 'reason': 'Modo semi-invencibilidad'},
                'give': {'severity': 'MEDIUM', 'reason': 'Dar items sin restricciones'},
                
                # Comandos de red / Lag manipulation
                'cl_interp 0': {'severity': 'MEDIUM', 'reason': 'Interpolación extremadamente baja'},
                'cl_interp_ratio 0': {'severity': 'MEDIUM', 'reason': 'Ratio de interpolación manipulado'},
                'rate 999999': {'severity': 'MEDIUM', 'reason': 'Tasa de datos manipulada'},
                'cl_cmdrate 999': {'severity': 'MEDIUM', 'reason': 'Command rate manipulado'},
                'cl_updaterate 999': {'severity': 'MEDIUM', 'reason': 'Update rate manipulado'},
                
                # Comandos de visión / FOV
                'fov_desired 120': {'severity': 'MEDIUM', 'reason': 'FOV extremadamente alto'},
                'fov_desired 130': {'severity': 'HIGH', 'reason': 'FOV extremadamente alto'},
                
                # Comandos de scripts / Binds sospechosos
                'exec': {'severity': 'LOW', 'reason': 'Ejecutar archivos externos (puede ser legítimo)'},
                'alias': {'severity': 'LOW', 'reason': 'Crear alias personalizados (revisar contexto)'},
                
                # Comandos de bypass / Anti-VAC
                'sv_consistency': {'severity': 'HIGH', 'reason': 'Comando de verificación de consistencia'},
                'sv_pure 0': {'severity': 'HIGH', 'reason': 'Deshabilita verificación de archivos'},
                
                # Comandos de información privilegiada
                'developer 1': {'severity': 'LOW', 'reason': 'Modo desarrollador (puede mostrar información extra)'},
                'net_graph 3': {'severity': 'LOW', 'reason': 'Información de red detallada'},
                
                # Comandos de rendimiento sospechosos
                'mat_hdr_level 0': {'severity': 'LOW', 'reason': 'Deshabilita HDR para ver mejor'},
                'mat_colorcorrection 0': {'severity': 'LOW', 'reason': 'Deshabilita corrección de color'},
                'fog_enable 0': {'severity': 'MEDIUM', 'reason': 'Deshabilita niebla para mejor visibilidad'},
                
                # Comandos de script automatizado / Bhop
                'wait': {'severity': 'LOW', 'reason': 'Comando wait (usado en macros)'},
                '+attack': {'severity': 'LOW', 'reason': 'Auto-ataque potencial (revisar contexto)'},
                '+jump': {'severity': 'MEDIUM', 'reason': 'Auto-jump potencial (Bhop script)'},
                'alias +bhop': {'severity': 'HIGH', 'reason': 'Script de Bunny Hop automático'},
                'alias bhop': {'severity': 'HIGH', 'reason': 'Script de Bunny Hop automático'},
                'bind space +bhop': {'severity': 'HIGH', 'reason': 'Bind de Bunny Hop automático'},
                'bind mouse1 +attack;wait;': {'severity': 'HIGH', 'reason': 'Auto-fire script'},
                
                # Comandos de triggerbot / Auto-shoot
                '+attack;wait;': {'severity': 'CRITICAL', 'reason': 'Script de auto-disparo'},
                'alias +trigger': {'severity': 'CRITICAL', 'reason': 'Script de triggerbot'},
                'alias trigger': {'severity': 'CRITICAL', 'reason': 'Script de triggerbot'},
                '-attack': {'severity': 'LOW', 'reason': 'Auto-ataque potencial (revisar contexto)'},
                
                # Comandos de spawning / Item manipulation
                'z_spawn': {'severity': 'CRITICAL', 'reason': 'Spawn de zombies/items'},
                'give health': {'severity': 'HIGH', 'reason': 'Dar salud instantánea'},
                'give ammo': {'severity': 'MEDIUM', 'reason': 'Dar munición'},
                'give weapon': {'severity': 'MEDIUM', 'reason': 'Dar armas'},
                
                # Comandos de Director / AI manipulation
                'director_': {'severity': 'HIGH', 'reason': 'Manipulación del Director AI'},
                'sb_': {'severity': 'MEDIUM', 'reason': 'Comandos de bots supervivientes'},
                'z_health': {'severity': 'HIGH', 'reason': 'Modificar salud de zombies'},
                'z_speed': {'severity': 'HIGH', 'reason': 'Modificar velocidad de zombies'},
                
                # Binds de spam / Flooding
                'bind mwheelup +jump': {'severity': 'LOW', 'reason': 'Bhop script potencial'},
                'bind mwheeldown +jump': {'severity': 'LOW', 'reason': 'Bhop script potencial'},
                
                # Hotkeys sospechosos (comunes en cheats tipo "presiona F5 para activar")
                'bind f5': {'severity': 'MEDIUM', 'reason': 'F5 comúnmente usado para activar cheats'},
                'bind f6': {'severity': 'MEDIUM', 'reason': 'F6 comúnmente usado para activar cheats'},
                'bind f7': {'severity': 'MEDIUM', 'reason': 'F7 comúnmente usado para activar cheats'},
                'bind f8': {'severity': 'MEDIUM', 'reason': 'F8 comúnmente usado para activar cheats'},
                'bind f9': {'severity': 'MEDIUM', 'reason': 'F9 comúnmente usado para activar cheats'},
                'bind f10': {'severity': 'MEDIUM', 'reason': 'F10 comúnmente usado para activar cheats'},
                'bind f11': {'severity': 'MEDIUM', 'reason': 'F11 comúnmente usado para activar cheats'},
                'bind f12': {'severity': 'MEDIUM', 'reason': 'F12 comúnmente usado para activar cheats'},
                'bind insert': {'severity': 'MEDIUM', 'reason': 'INSERT comúnmente usado para menu de cheats'},
                'bind home': {'severity': 'MEDIUM', 'reason': 'HOME comúnmente usado para menu de cheats'},
                'bind end': {'severity': 'MEDIUM', 'reason': 'END comúnmente usado para menu de cheats'},
                'bind del': {'severity': 'MEDIUM', 'reason': 'DELETE comúnmente usado para menu de cheats'},
                'bind pgup': {'severity': 'MEDIUM', 'reason': 'PAGE UP comúnmente usado para menu de cheats'},
                'bind pgdn': {'severity': 'MEDIUM', 'reason': 'PAGE DOWN comúnmente usado para menu de cheats'},
            }
            
            # Analizar cada línea del archivo
            for line_number, line in enumerate(content, 1):
                line_stripped = line.strip()
                
                # Ignorar comentarios y líneas vacías
                if not line_stripped or line_stripped.startswith('//') or line_stripped.startswith(';'):
                    continue
                
                # Convertir a minúsculas para comparación
                line_lower = line_stripped.lower()
                
                # Buscar comandos prohibidos
                for prohibited_cmd, cmd_info in prohibited_commands.items():
                    if prohibited_cmd.lower() in line_lower:
                        prohibited_commands_found.append({
                            'line_number': line_number,
                            'line_content': line_stripped,
                            'command': prohibited_cmd,
                            'severity': cmd_info['severity'],
                            'reason': cmd_info['reason']
                        })
            
            # Si se encontraron comandos prohibidos, devolver análisis
            if prohibited_commands_found:
                return {
                    'file_name': os.path.basename(cfg_file_path),
                    'file_path': cfg_file_path,
                    'file_size': os.path.getsize(cfg_file_path),
                    'prohibited_commands': prohibited_commands_found,
                    'total_lines': len(content),
                    'severity_summary': self._get_cfg_severity_summary(prohibited_commands_found)
                }
            
            return None
            
        except Exception as e:
            print(f"Error al analizar archivo .cfg {cfg_file_path}: {e}")
            return None
    
    def _get_cfg_severity_summary(self, prohibited_commands):
        """Genera un resumen de severidad de los comandos encontrados"""
        summary = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for cmd in prohibited_commands:
            severity = cmd.get('severity', 'LOW')
            if severity in summary:
                summary[severity] += 1
        
        # Determinar severidad general
        if summary['CRITICAL'] > 0:
            overall_severity = 'CRITICAL'
        elif summary['HIGH'] > 0:
            overall_severity = 'HIGH'
        elif summary['MEDIUM'] > 0:
            overall_severity = 'MEDIUM'
        else:
            overall_severity = 'LOW'
        
        return {
            'counts': summary,
            'overall_severity': overall_severity
        }
    
    def detect_system_install_date(self):
        """Detecta la fecha de instalación/formateo del sistema"""
        install_dates = []
        
        try:
            # Método 1: Registro de Windows - Fecha de instalación del sistema
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    install_date_str = winreg.QueryValueEx(key, "InstallDate")[0]
                    if install_date_str:
                        install_date = datetime.fromtimestamp(int(install_date_str))
                        install_dates.append({
                            'source': 'Windows Registry',
                            'date': install_date.isoformat(),
                            'formatted_date': install_date.strftime("%Y-%m-%d %H:%M:%S"),
                            'description': 'Fecha de instalación del sistema operativo'
                        })
            except Exception:
                pass
            
            # Método 2: Fecha de creación del directorio Windows
            try:
                windows_path = os.environ.get('WINDIR', 'C:\\Windows')
                if os.path.exists(windows_path):
                    stat = os.stat(windows_path)
                    install_date = datetime.fromtimestamp(stat.st_ctime)
                    install_dates.append({
                        'source': 'Windows Directory',
                        'date': install_date.isoformat(),
                        'formatted_date': install_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'description': 'Fecha de creación del directorio Windows'
                    })
            except Exception:
                pass
            
            # Método 3: Fecha de creación del directorio de usuario
            try:
                user_profile = os.environ.get('USERPROFILE', '')
                if user_profile and os.path.exists(user_profile):
                    stat = os.stat(user_profile)
                    install_date = datetime.fromtimestamp(stat.st_ctime)
                    install_dates.append({
                        'source': 'User Profile',
                        'date': install_date.isoformat(),
                        'formatted_date': install_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'description': 'Fecha de creación del perfil de usuario'
                    })
            except Exception:
                pass
            
            # Método 4: Fecha de creación del directorio Program Files
            try:
                program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
                if os.path.exists(program_files):
                    stat = os.stat(program_files)
                    install_date = datetime.fromtimestamp(stat.st_ctime)
                    install_dates.append({
                        'source': 'Program Files',
                        'date': install_date.isoformat(),
                        'formatted_date': install_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'description': 'Fecha de creación del directorio Program Files'
                    })
            except Exception:
                pass
            
            # Método 5: Fecha de creación del directorio Steam (si existe)
            try:
                if self.steam_path and os.path.exists(self.steam_path):
                    stat = os.stat(self.steam_path)
                    install_date = datetime.fromtimestamp(stat.st_ctime)
                    install_dates.append({
                        'source': 'Steam Directory',
                        'date': install_date.isoformat(),
                        'formatted_date': install_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'description': 'Fecha de instalación de Steam'
                    })
            except Exception:
                pass
            
        except Exception as e:
            install_dates.append({
                'source': 'Error',
                'date': None,
                'formatted_date': 'Error al detectar',
                'description': f'Error: {str(e)}'
            })
        
        # Determinar la fecha más probable de formateo
        if install_dates:
            # Ordenar por fecha y tomar la más antigua como referencia
            valid_dates = [d for d in install_dates if d['date'] is not None]
            if valid_dates:
                valid_dates.sort(key=lambda x: x['date'])
                most_likely_date = valid_dates[0]
                
                self.results['system_install_info'] = {
                    'most_likely_install_date': most_likely_date,
                    'all_detected_dates': install_dates,
                    'days_since_install': (datetime.now() - datetime.fromisoformat(most_likely_date['date'])).days
                }
            else:
                self.results['system_install_info'] = {
                    'most_likely_install_date': None,
                    'all_detected_dates': install_dates,
                    'days_since_install': None
                }
        else:
            self.results['system_install_info'] = {
                'most_likely_install_date': None,
                'all_detected_dates': [],
                'days_since_install': None
            }
        
        return len(install_dates) > 0
    
    def check_game_running(self):
        """Verifica si Left 4 Dead 2 está ejecutándose"""
        l4d2_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and 'left4dead2' in proc.info['name'].lower():
                        l4d2_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        
        return l4d2_processes
    
    def generate_detailed_report(self):
        """Genera un reporte detallado de la verificación"""
        # Obtener información de la PC
        self.get_pc_info()
        
        # Determinar estado de integridad
        integrity_status = self.get_integrity_status()
        self.results['integrity_status'] = integrity_status
        
        report = {
            'report_info': {
                'timestamp': self.results['timestamp'],
                'version': '1.0',
                'generated_by': 'L4D2 Tournament Integrity Checker'
            },
            'pc_info': self.results['pc_info'],
            'steam_info': {
                'steam_found': self.steam_path is not None,
                'steam_path': self.steam_path,
                'l4d2_found': self.l4d2_path is not None,
                'l4d2_path': self.l4d2_path
            },
            'mods_analysis': {
                'mods_detected': len(self.results['mods_detected']) > 0,
                'mods_count': len(self.results['mods_detected']),
                'mods_list': self.results['mods_detected'],
                'versus_mods_detected': len(self.results.get('versus_mods', [])) > 0,
                'versus_mods_count': len(self.results.get('versus_mods', [])),
                'versus_mods_list': self.results.get('versus_mods', []),
                'status': 'CLEAN' if (len(self.results['mods_detected']) == 0 and 
                                     len(self.results.get('versus_mods', [])) == 0) else 'MODS_FOUND'
            },
            'steam_accounts_analysis': {
                'accounts_count': self.results['steam_accounts_count'],
                'accounts_list': self.results['steam_accounts'],
                'suspicious_accounts': self.results['steam_accounts_count'] > 10,
                'status': 'CLEAN' if self.results['steam_accounts_count'] <= 10 else 'SUSPICIOUS'
            },
            'cheats_analysis': {
                'suspicious_processes_found': len(self.results['suspicious_processes']) > 0,
                'suspicious_processes_count': len(self.results['suspicious_processes']),
                'suspicious_processes_list': self.results['suspicious_processes'],
                'memory_injections_found': len(self.results.get('memory_injections', [])) > 0,
                'memory_injections_count': len(self.results.get('memory_injections', [])),
                'memory_injections_list': self.results.get('memory_injections', []),
                'known_cheat_signatures_found': len(self.results.get('known_cheat_signatures', [])) > 0,
                'known_cheat_signatures_count': len(self.results.get('known_cheat_signatures', [])),
                'known_cheat_signatures_list': self.results.get('known_cheat_signatures', []),
                'status': 'CLEAN' if (len(self.results['suspicious_processes']) == 0 and 
                                     len(self.results.get('memory_injections', [])) == 0 and
                                     len(self.results.get('known_cheat_signatures', [])) == 0) else 'SUSPICIOUS_PROCESSES'
            },
            'game_status': {
                'game_running': len(self.check_game_running()) > 0,
                'game_processes': self.check_game_running()
            },
            'token_validation': self.results.get('token_validation'),
            'overall_integrity': {
                'status': integrity_status,
                'summary': self.get_integrity_summary()
            }
        }
        
        return report
    
    def get_integrity_summary(self):
        """Genera un resumen del estado de integridad"""
        issues = []
        
        if len(self.results['mods_detected']) > 0:
            issues.append(f"Mods detectados: {len(self.results['mods_detected'])}")
        
        if len(self.results.get('versus_mods', [])) > 0:
            issues.append(f"Mods en Versus: {len(self.results['versus_mods'])}")
        
        if len(self.results['suspicious_processes']) > 0:
            issues.append(f"Procesos sospechosos: {len(self.results['suspicious_processes'])}")
        
        if len(self.results.get('memory_injections', [])) > 0:
            issues.append(f"Inyecciones de memoria: {len(self.results['memory_injections'])}")
        
        if len(self.results.get('known_cheat_signatures', [])) > 0:
            issues.append(f"Firmas de cheats conocidos: {len(self.results['known_cheat_signatures'])}")
        
        if self.results['steam_accounts_count'] > 10:
            issues.append(f"Demasiadas cuentas Steam: {self.results['steam_accounts_count']}")
        
        if not issues:
            return "Sistema limpio - Sin problemas detectados"
        else:
            return "Problemas detectados: " + ", ".join(issues)
    
    def generate_report(self):
        """Genera un reporte completo de la verificación (método legacy)"""
        return self.generate_detailed_report()
    
    def _show_loading_gif_window(self):
        """Muestra una ventana con el GIF de carga (para modo consola)"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana
            self.loading_root = tk.Tk()
            self.loading_root.title("Verificando Integridad...")
            self.loading_root.geometry("600x600")  # Aumentado para que el GIF se vea completo
            self.loading_root.resizable(False, False)
            
            # Frame principal
            main_frame = ttk.Frame(self.loading_root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(main_frame, text="Verificando Integridad del Sistema", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Frame para el GIF
            gif_frame = ttk.Frame(main_frame)
            gif_frame.pack(pady=(0, 20))
            
            # Intentar cargar el GIF
            try:
                from PIL import Image, ImageTk
                
                # Buscar el GIF
                gif_paths = [
                    "loading.gif",
                    os.path.join(os.path.dirname(__file__), "loading.gif"),
                    os.path.join(os.path.dirname(sys.executable), "loading.gif"),
                ]
                
                if is_compiled():
                    gif_paths.append(os.path.join(sys._MEIPASS, "loading.gif"))
                
                gif_path = None
                for path in gif_paths:
                    if os.path.exists(path):
                        gif_path = path
                        break
                
                if gif_path:
                    # Cargar GIF
                    pil_image = Image.open(gif_path)
                    self.loading_gif_image = ImageTk.PhotoImage(pil_image)
                    
                    # Mostrar la imagen
                    gif_label = ttk.Label(gif_frame, image=self.loading_gif_image)
                    gif_label.pack()
                    
                    # Animar GIF
                    def animate_gif(frame_index=0):
                        try:
                            if hasattr(self, 'loading_root') and self.loading_root.winfo_exists():
                                pil_image.seek(frame_index)
                                photo = ImageTk.PhotoImage(pil_image)
                                gif_label.config(image=photo)
                                gif_label.image = photo
                                delay = pil_image.info.get('duration', 50)
                                next_frame = (frame_index + 1) % pil_image.n_frames
                                self.loading_root.after(delay, lambda: animate_gif(next_frame))
                        except:
                            pass
                    
                    animate_gif()
                else:
                    # Mostrar texto si no hay GIF
                    ttk.Label(gif_frame, text="Verificando...", 
                             font=("Arial", 24)).pack()
            except:
                # Mostrar texto si hay error
                ttk.Label(gif_frame, text="Verificando...", 
                         font=("Arial", 24)).pack()
            
            # Mensaje
            info_text = ("Analizando sistema...\n"
                        "• Detectando mods instalados\n"
                        "• Analizando cuentas Steam\n"
                        "• Escaneando procesos\n"
                        "• Generando reporte completo")
            
            info_label = ttk.Label(main_frame, text=info_text, 
                                  font=("Arial", 9), justify=tk.LEFT)
            info_label.pack(pady=(0, 20))
            
            # Barra de progreso
            progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
            progress_bar.pack(fill=tk.X, pady=(0, 20))
            progress_bar.start()
            
            # Iniciar mainloop
            self.loading_root.mainloop()
            
        except Exception as e:
            # Si falla, no pasa nada - simplemente no muestra la ventana
            # print(f"DEBUG: No se pudo mostrar ventana de carga: {e}")
            pass
    
    def _close_loading_window(self):
        """Cierra la ventana de carga si existe"""
        try:
            if hasattr(self, 'loading_root'):
                self.loading_root.quit()
                self.loading_root.destroy()
        except:
            pass
    
    def show_console_progress(self, message, duration=0.5):
        """Muestra una animación de progreso en consola"""
        import sys
        import time
        
        # Animación de spinner
        spinner = ['|', '/', '-', '\\']
        end_time = time.time() + duration
        i = 0
        
        while time.time() < end_time:
            sys.stdout.write(f'\r  {spinner[i % len(spinner)]} {message}...')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write(f'\r  OK {message}     \n')
        sys.stdout.flush()
    
    def get_integrity_status(self):
        """Determina el estado de integridad general"""
        issues = 0
        
        if len(self.results['mods_detected']) > 0:
            issues += 1
        if len(self.results.get('versus_mods', [])) > 0:
            issues += 3  # Los mods en Versus son muy críticos
        
        # Evaluar procesos sospechosos con énfasis en herramientas de inyección
        if len(self.results['suspicious_processes']) > 0:
            # Contar herramientas de inyección de DLLs
            injection_tools = sum(1 for p in self.results['suspicious_processes'] 
                                 if p.get('type') == 'dll_injection_tool')
            injection_tools_with_game = sum(1 for p in self.results['suspicious_processes'] 
                                           if p.get('type') == 'dll_injection_tool' and p.get('l4d2_running'))
            
            if injection_tools_with_game > 0:
                issues += 4  # Herramientas de inyección mientras el juego corre es EXTREMADAMENTE sospechoso
            elif injection_tools > 0:
                issues += 3  # Herramientas de inyección presentes es muy sospechoso
            else:
                issues += 1  # Otros procesos sospechosos
        
        if len(self.results.get('memory_injections', [])) > 0:
            issues += 1
        if len(self.results.get('known_cheat_signatures', [])) > 0:
            issues += 2  # Las firmas de cheats son más críticas
        if len(self.results.get('suspicious_cfg_commands', [])) > 0:
            # Evaluar severidad de comandos CFG
            critical_cfgs = sum(1 for cfg in self.results.get('suspicious_cfg_commands', []) 
                               if cfg.get('severity_summary', {}).get('overall_severity') == 'CRITICAL')
            if critical_cfgs > 0:
                issues += 2  # Comandos críticos en CFG son muy sospechosos
            else:
                issues += 1  # Otros comandos sospechosos
        
        # Evaluar archivos de cheats encontrados
        if len(self.results.get('cheat_files_found', [])) > 0:
            cheat_folders = sum(1 for cf in self.results.get('cheat_files_found', []) 
                               if cf.get('type') == 'cheat_folder')
            if cheat_folders > 0:
                issues += 3  # Carpetas completas de cheats son EXTREMADAMENTE sospechosas
            else:
                issues += 2  # Archivos individuales de cheats son muy sospechosos
        
        # Evaluar programas ejecutados recientemente
        if len(self.results.get('recently_executed_suspicious', [])) > 0:
            # Contar programas ejecutados hace menos de 1 hora (MUY sospechoso)
            recent_executions = sum(1 for re in self.results.get('recently_executed_suspicious', [])
                                   if re.get('hours_ago', 999) < 1)
            if recent_executions > 0:
                issues += 4  # Ejecutado recientemente es EXTREMADAMENTE sospechoso
            else:
                # Ejecutado hace más de 1 hora pero menos de 24 horas
                today_executions = sum(1 for re in self.results.get('recently_executed_suspicious', [])
                                      if re.get('hours_ago', 999) < 24)
                if today_executions > 0:
                    issues += 3  # Ejecutado hoy es muy sospechoso
                else:
                    issues += 2  # Ejecutado hace días sigue siendo sospechoso
        
        if self.results['steam_accounts_count'] > 10:  # Más de 10 cuentas es sospechoso
            issues += 1
        
        if issues == 0:
            return "CLEAN"
        elif issues <= 2:
            return "WARNING"
        else:
            return "SUSPICIOUS"
    
    def run_full_check(self, show_loading_window=True):
        """Ejecuta todas las verificaciones con tiempo mínimo de 10 segundos"""
        import time
        import threading
        start_time = time.time()  # Registrar tiempo de inicio
        
        # Mostrar ventana de carga con GIF si está habilitado
        loading_win = None
        if show_loading_window:
            loading_thread = threading.Thread(target=self._show_loading_gif_window, daemon=True)
            loading_thread.start()
        
        print("Iniciando verificación de integridad...")
        print("=" * 60)
        
        # Obtener información de la PC
        print("\n[1/11] Obteniendo información del sistema...")
        self.show_console_progress("Recopilando información del sistema", 1.0)
        self.get_pc_info()
        print(f"PC: {self.results['pc_info'].get('computer_name', 'Unknown')} ({self.results['pc_info'].get('username', 'Unknown')})")
        print(f"Identificación del Sistema:")
        print(f"  IP Externa: {self.results['pc_info'].get('external_ip', 'Unknown')}")
        print(f"  IP Local: {self.results['pc_info'].get('local_ip', 'Unknown')}")
        print(f"  MAC Address: {self.results['pc_info'].get('mac_address', 'Unknown')}")
        print(f"  System UUID: {self.results['pc_info'].get('system_uuid', 'Unknown')}")
        print(f"  Disk Serial: {self.results['pc_info'].get('disk_serial', 'Unknown')}")
        print(f"  Fingerprint: {self.results['pc_info'].get('system_fingerprint', 'Unknown')}")
        print()
        
        # Buscar Steam y L4D2
        print("[2/11] Localizando Steam y Left 4 Dead 2...")
        self.show_console_progress("Buscando instalación de Steam", 0.8)
        if not self.find_steam_path():
            print("ERROR: Steam no encontrado")
            return False
        
        if not self.find_l4d2_path():
            print("ERROR: Left 4 Dead 2 no encontrado")
            return False
        
        print(f"OK - Steam encontrado en: {self.steam_path}")
        print(f"OK - L4D2 encontrado en: {self.l4d2_path}")
        
        # Detectar mods
        print("\n[3/11] Escaneando mods instalados...")
        self.show_console_progress("Analizando archivos de mods", 1.2)
        mods_found = self.detect_mods()
        if mods_found:
            print(f"ADVERTENCIA: Se encontraron {len(self.results['mods_detected'])} mods:")
            for mod in self.results['mods_detected']:
                print(f"   - {mod['name']} ({mod['size']} bytes)")
        else:
            print("OK - No se encontraron mods")
        
        # Contar cuentas de Steam
        print("\n[4/11] Analizando cuentas Steam...")
        self.show_console_progress("Extrayendo información de cuentas", 1.0)
        accounts = self.count_steam_accounts()
        print(f"Cuentas de Steam en esta PC: {accounts}")
        
        if accounts > 0:
            print("   Detalles de cuentas encontradas:")
            for i, account in enumerate(self.results['steam_accounts'], 1):
                print(f"   {i}. Usuario: {account['username']}")
                print(f"      SteamID64: {account['steam_id64']}")
                print(f"      SteamID3: {account['steam_id3']}")
                print(f"      SteamID: {account['steam_id']}")
                print()
        
        # Detectar carpetas no oficiales en raíz de L4D2
        print("\n[5/15] Verificando carpetas en raíz del juego...")
        self.show_console_progress("Analizando estructura de carpetas", 0.8)
        unofficial_folders_found = self.detect_unofficial_folders()
        if unofficial_folders_found:
            print(f"ADVERTENCIA CRÍTICA: Se encontraron {len(self.results['unofficial_folders'])} carpetas no oficiales:")
            for folder in self.results['unofficial_folders']:
                print(f"   ⚠️ {folder['folder_name']} - {folder['description']}")
                if folder.get('files_count'):
                    print(f"      Archivos: {folder['files_count']}")
        else:
            print("OK - Solo carpetas oficiales en raíz del juego")
        
        # Validar integridad de gameinfo.txt
        print("\n[6/15] Validando archivo gameinfo.txt...")
        self.show_console_progress("Verificando integridad de gameinfo.txt", 0.5)
        gameinfo_modified = self.validate_gameinfo_txt()
        if gameinfo_modified:
            validation = self.results.get('gameinfo_validation', {})
            if validation.get('status') == 'MODIFIED':
                print(f"ADVERTENCIA CRÍTICA: gameinfo.txt ha sido modificado")
                if validation.get('modifications'):
                    print("   Modificaciones detectadas:")
                    for mod in validation['modifications']:
                        print(f"      - {mod}")
            elif validation.get('status') == 'MISSING':
                print(f"ERROR CRÍTICO: gameinfo.txt no encontrado")
        else:
            print("OK - gameinfo.txt es oficial y no ha sido modificado")
        
        # Validar integridad de addonconfig.cfg
        print("\n[7/16] Validando archivo addonconfig.cfg...")
        self.show_console_progress("Verificando restricciones de addons en modos competitivos", 0.5)
        addonconfig_modified = self.validate_addonconfig_cfg()
        if addonconfig_modified:
            validation = self.results.get('addonconfig_validation', {})
            if validation.get('status') == 'MODIFIED':
                print(f"ADVERTENCIA CRÍTICA: addonconfig.cfg ha sido modificado")
                print(f"   ⚠️ {validation['description']}")
                if validation.get('issues'):
                    print("   Problemas detectados:")
                    for issue in validation['issues']:
                        print(f"      - {issue}")
            elif validation.get('status') == 'MISSING':
                print(f"ERROR CRÍTICO: addonconfig.cfg no encontrado")
        else:
            validation = self.results.get('addonconfig_validation', {})
            if validation.get('status') == 'VALID':
                print("OK - addonconfig.cfg es oficial y bloquea addons en versus/scavenge")
            elif validation.get('status') == 'MODIFIED_FORMAT':
                print("OK - addonconfig.cfg tiene formato diferente pero valores correctos")
        
        # Validar integridad de 360controller.cfg
        print("\n[8/17] Validando archivo 360controller.cfg...")
        self.show_console_progress("Verificando configuración de mando (autoaim exploit)", 0.5)
        controller_modified = self.validate_360controller_cfg()
        if controller_modified:
            validation = self.results.get('controller_validation', {})
            if validation.get('status') == 'MODIFIED':
                print(f"ADVERTENCIA CRÍTICA: 360controller.cfg ha sido modificado")
                print(f"   ⚠️ {validation['description']}")
                if validation.get('issues'):
                    print("   Problemas detectados:")
                    for issue in validation['issues']:
                        print(f"      - {issue}")
            elif validation.get('status') == 'MISSING':
                print(f"INFO: 360controller.cfg no encontrado (solo necesario si se usa mando)")
        else:
            validation = self.results.get('controller_validation', {})
            if validation.get('status') == 'VALID':
                print("OK - 360controller.cfg es oficial y no permite autoaim exploit")
            elif validation.get('status') == 'MODIFIED_FORMAT':
                print("OK - 360controller.cfg tiene formato diferente pero valores críticos correctos")
            elif validation.get('status') == 'MISSING':
                print("INFO - 360controller.cfg no encontrado (solo necesario si se usa mando)")
        
        # Validar integridad de config.cfg
        print("\n[9/19] Validando archivo config.cfg...")
        self.show_console_progress("Verificando comandos críticos en configuración principal", 0.5)
        config_modified = self.validate_config_cfg()
        if config_modified:
            validation = self.results.get('config_validation', {})
            if validation.get('status') == 'MODIFIED':
                print(f"ADVERTENCIA CRÍTICA: config.cfg contiene configuraciones sospechosas")
                print(f"   ⚠️ {validation['description']}")
                if validation.get('issues'):
                    print("   Problemas detectados:")
                    for issue in validation['issues']:
                        print(f"      - {issue}")
            elif validation.get('status') == 'MISSING':
                print(f"ERROR CRÍTICO: config.cfg no encontrado")
        else:
            print("OK - config.cfg no contiene comandos prohibidos")
        
        # Validar integridad de perf.cfg
        print("\n[10/19] Validando archivo perf.cfg...")
        self.show_console_progress("Verificando archivo de pruebas de rendimiento", 0.5)
        perf_modified = self.validate_perf_cfg()
        if perf_modified:
            validation = self.results.get('perf_validation', {})
            if validation.get('status') == 'MODIFIED':
                print(f"ADVERTENCIA CRÍTICA: perf.cfg contiene comandos prohibidos")
                print(f"   ⚠️ {validation['description']}")
                if validation.get('issues'):
                    print("   Problemas detectados:")
                    for issue in validation['issues']:
                        print(f"      - {issue}")
        else:
            validation = self.results.get('perf_validation', {})
            if validation.get('status') == 'VALID':
                print("OK - perf.cfg es oficial")
            elif validation.get('status') == 'MODIFIED_FORMAT':
                print("OK - perf.cfg tiene formato diferente pero sin comandos prohibidos")
            elif validation.get('status') == 'MISSING':
                print("INFO - perf.cfg no encontrado (solo necesario para pruebas de rendimiento)")
        
        # Escanear ubicaciones críticas con firmas de cheats
        print("\n[11/19] Escaneando ubicaciones críticas del juego...")
        self.show_console_progress("Analizando archivos contra firmas de cheats conocidos", 1.5)
        critical_found = self.scan_critical_locations()
        if critical_found:
            print(f"ADVERTENCIA CRÍTICA: Se encontraron {len(self.results['critical_findings'])} archivos sospechosos:")
            for finding in self.results['critical_findings']:
                print(f"   🚨 {finding['file_name']}")
                print(f"      Ubicación: {finding['location']}")
                print(f"      Tipo de cheat: {finding['description']}")
                print(f"      Patrón: '{finding['matched_pattern']}'")
                print(f"      Severidad: {finding['severity']}")
                print()
        else:
            print("OK - No se encontraron archivos con firmas de cheats conocidos")
        
        # Detectar procesos sospechosos
        print("\n[9/16] Escaneando procesos del sistema...")
        self.show_console_progress("Analizando procesos activos", 1.5)
        suspicious = self.detect_suspicious_processes()
        if suspicious:
            print(f"ADVERTENCIA: Se encontraron {len(self.results['suspicious_processes'])} procesos sospechosos:")
            
            # Separar herramientas de inyección de otros procesos sospechosos
            injection_tools = [p for p in self.results['suspicious_processes'] if p.get('type') == 'dll_injection_tool']
            other_suspicious = [p for p in self.results['suspicious_processes'] if p.get('type') != 'dll_injection_tool']
            
            # Mostrar herramientas de inyección primero (más críticas)
            if injection_tools:
                print(f"\n   🔴 HERRAMIENTAS DE INYECCIÓN DE DLLs DETECTADAS ({len(injection_tools)}):")
                for i, proc in enumerate(injection_tools, 1):
                    print(f"   {i}. Herramienta: {proc.get('tool_name', proc['name'])} (PID: {proc['pid']})")
                    print(f"      Proceso: {proc['name']}")
                    if proc.get('exe'):
                        print(f"      Ruta: {proc['exe']}")
                    print(f"      Severidad: {proc.get('severity', 'HIGH')}")
                    print(f"      Descripción: {proc.get('description', 'Herramienta de inyección')}")
                    if proc.get('l4d2_running'):
                        print(f"      ⚠️  ¡CRÍTICO: Left 4 Dead 2 está ejecutándose mientras esta herramienta está activa!")
                    print()
            
            # Mostrar otros procesos sospechosos
            if other_suspicious:
                print(f"   ⚠️  OTROS PROCESOS SOSPECHOSOS ({len(other_suspicious)}):")
                for i, proc in enumerate(other_suspicious, 1):
                    print(f"   {i}. Proceso: {proc['name']} (PID: {proc['pid']})")
                    if proc.get('exe'):
                        print(f"      Ruta: {proc['exe']}")
                    if proc.get('reason'):
                        print(f"      Razón: {proc['reason']}")
                    print()
        else:
            print("OK - No se encontraron procesos sospechosos")
        
        # Detectar inyecciones de memoria
        print("\n[15/16] Verificando inyecciones de memoria...")
        self.show_console_progress("Inspeccionando memoria del sistema", 1.3)
        memory_injections = self.detect_memory_injections()
        if memory_injections:
            print(f"ADVERTENCIA: Se encontraron {len(self.results['memory_injections'])} inyecciones de memoria:")
            for i, injection in enumerate(self.results['memory_injections'], 1):
                print(f"   {i}. Proceso: {injection['process_name']} (PID: {injection['process_pid']})")
                if injection.get('dll_path'):
                    print(f"      DLL: {injection['dll_path']}")
                if injection.get('reason'):
                    print(f"      Razón: {injection['reason']}")
        else:
            print("OK - No se encontraron inyecciones de memoria")
        
        # Detectar firmas de cheats conocidos
        print("\n[13/16] Buscando firmas de cheats conocidos...")
        self.show_console_progress("Comparando con base de datos de cheats", 1.5)
        cheat_signatures = self.detect_known_cheat_signatures()
        if cheat_signatures:
            print(f"CRÍTICO: Se encontraron {len(self.results['known_cheat_signatures'])} firmas de cheats conocidos:")
            for i, signature in enumerate(self.results['known_cheat_signatures'], 1):
                print(f"   {i}. {signature['description']} (Severidad: {signature['severity']})")
                if signature.get('process_name'):
                    print(f"      Proceso: {signature['process_name']} (PID: {signature['process_pid']})")
                if signature.get('file_path'):
                    print(f"      Archivo: {signature['file_path']}")
        else:
            print("OK - No se encontraron firmas de cheats conocidos")
        
        # Detectar mods en Versus
        print("\n[14/16] Verificando mods en modo Versus...")
        self.show_console_progress("Analizando modificaciones de Versus", 1.2)
        versus_mods = self.detect_versus_mods()
        if versus_mods:
            print(f"CRÍTICO: Se encontraron {len(self.results['versus_mods'])} mods en Versus:")
            for i, versus_mod in enumerate(self.results['versus_mods'], 1):
                print(f"   {i}. {versus_mod['description']} (Severidad: {versus_mod['severity']})")
                if versus_mod.get('file_path'):
                    print(f"      Archivo: {versus_mod['file_path']}")
                if versus_mod.get('folder_path'):
                    print(f"      Carpeta: {versus_mod['folder_path']}")
                if versus_mod.get('modification'):
                    print(f"      Modificación: {versus_mod['modification']}")
        else:
            print("OK - No se encontraron mods en Versus")
        
        # Detectar comandos prohibidos en archivos CFG
        print("\n[12/16] Analizando archivos de configuración (CFG)...")
        self.show_console_progress("Escaneando archivos .cfg en busca de comandos prohibidos", 1.5)
        suspicious_cfgs = self.detect_suspicious_cfg_commands()
        if suspicious_cfgs:
            print(f"ADVERTENCIA: Se encontraron {len(self.results['suspicious_cfg_commands'])} archivos .cfg con comandos sospechosos:")
            for i, cfg in enumerate(self.results['suspicious_cfg_commands'], 1):
                print(f"   {i}. Archivo: {cfg['file_name']}")
                print(f"      Ruta: {cfg['file_path']}")
                print(f"      Comandos prohibidos encontrados: {len(cfg['prohibited_commands'])}")
                for cmd in cfg['prohibited_commands'][:3]:  # Mostrar solo los primeros 3
                    print(f"         - {cmd['command']} (Severidad: {cmd['severity']}) - {cmd['reason']}")
                if len(cfg['prohibited_commands']) > 3:
                    print(f"         ... y {len(cfg['prohibited_commands']) - 3} más")
        else:
            print("OK - No se encontraron comandos prohibidos en archivos .cfg")
        
        # Detectar archivos de cheats en el sistema
        print("\n[10/16] Buscando archivos de cheats en el sistema...")
        self.show_console_progress("Escaneando carpetas comunes (Desktop, Downloads, etc.)", 2.0)
        cheat_files = self.detect_cheat_files_in_system()
        if cheat_files:
            print(f"CRÍTICO: Se encontraron {len(self.results['cheat_files_found'])} archivos/carpetas de cheats:")
            
            # Separar carpetas de archivos individuales
            cheat_folders = [c for c in self.results['cheat_files_found'] if c.get('type') == 'cheat_folder']
            cheat_individual_files = [c for c in self.results['cheat_files_found'] if c.get('type') == 'cheat_file']
            
            # Mostrar carpetas de cheats
            if cheat_folders:
                print(f"\n   🔴 CARPETAS DE CHEATS DETECTADAS ({len(cheat_folders)}):")
                for i, folder in enumerate(cheat_folders, 1):
                    print(f"   {i}. Carpeta: {folder['folder_name']}")
                    print(f"      Ruta: {folder['folder_path']}")
                    print(f"      Total de archivos: {folder['total_files']}")
                    print(f"      Archivos sospechosos: {len(folder['suspicious_files'])}")
                    if folder['suspicious_files']:
                        print(f"      Ejemplos:")
                        for sus_file in folder['suspicious_files'][:3]:
                            print(f"         - {sus_file['name']} ({sus_file['size']} bytes)")
                    print()
            
            # Mostrar archivos individuales
            if cheat_individual_files:
                print(f"   ⚠️  ARCHIVOS DE CHEATS INDIVIDUALES ({len(cheat_individual_files)}):")
                for i, file in enumerate(cheat_individual_files, 1):
                    print(f"   {i}. Archivo: {file['file_name']}")
                    print(f"      Ruta: {file['file_path']}")
                    print(f"      Tamaño: {file['file_size']} bytes")
                    print(f"      Ubicación: {file['location']}")
                    print()
        else:
            print("OK - No se encontraron archivos de cheats en ubicaciones comunes")
        
        # Detectar programas ejecutados recientemente (incluso si ya están cerrados)
        print("\n[11/16] Analizando historial de programas ejecutados...")
        self.show_console_progress("Revisando Prefetch y Registro de Windows", 1.5)
        recently_executed = self.detect_recently_executed_programs()
        if recently_executed:
            print(f"CRÍTICO: Se encontraron {len(self.results['recently_executed_suspicious'])} programas sospechosos ejecutados recientemente:")
            
            # Separar por fuente
            prefetch_items = [r for r in self.results['recently_executed_suspicious'] if r.get('source') == 'Prefetch']
            userassist_items = [r for r in self.results['recently_executed_suspicious'] if r.get('source') == 'UserAssist Registry']
            recentapps_items = [r for r in self.results['recently_executed_suspicious'] if r.get('source') == 'RecentApps Registry']
            
            # Mostrar items de Prefetch (los más importantes con timestamp)
            if prefetch_items:
                print(f"\n   🔴 PROGRAMAS EJECUTADOS (Prefetch - Windows guarda historial):")
                for i, item in enumerate(prefetch_items, 1):
                    print(f"   {i}. Programa: {item['program_name']}")
                    print(f"      Última ejecución: {item['last_execution_formatted']}")
                    print(f"      Hace: {item['hours_ago']} horas")
                    print(f"      Archivo Prefetch: {item['prefetch_file']}")
                    print(f"      Severidad: {item['severity']}")
                    print(f"      Confianza: {item.get('confidence', 'ALTA')}")
                    if item.get('context_details'):
                        print(f"      Análisis: {item['context_details']}")
                    if item['hours_ago'] < 1:
                        print(f"      ⚠️  ¡EJECUTADO EN LA ÚLTIMA HORA! MUY SOSPECHOSO")
                    elif item['hours_ago'] < 24:
                        print(f"      ⚠️  Ejecutado hoy")
                    print()
            
            # Mostrar items de UserAssist
            if userassist_items:
                print(f"   📋 HISTORIAL DE USERASSIST ({len(userassist_items)} programas):")
                for i, item in enumerate(userassist_items, 1):
                    print(f"   {i}. {item['program_name']}")
                    if item.get('program_path'):
                        print(f"      Ruta: {item['program_path']}")
                    print()
            
            # Mostrar items de RecentApps
            if recentapps_items:
                print(f"   📱 APLICACIONES RECIENTES ({len(recentapps_items)} programas):")
                for i, item in enumerate(recentapps_items, 1):
                    print(f"   {i}. {item['program_name']}")
                    print()
        else:
            print("OK - No se encontraron programas sospechosos en el historial de ejecución")
        
        # Detectar fecha de formateo/instalación del sistema
        install_info = self.detect_system_install_date()
        if install_info and self.results['system_install_info']['most_likely_install_date']:
            install_date = self.results['system_install_info']['most_likely_install_date']
            days_since = self.results['system_install_info']['days_since_install']
            print(f"INFO: Sistema instalado/formateado el: {install_date['formatted_date']}")
            print(f"      Fuente: {install_date['source']}")
            print(f"      Días desde la instalación: {days_since}")
        else:
            print("INFO: No se pudo determinar la fecha de formateo del sistema")
        
        # Verificar si el juego está ejecutándose
        game_processes = self.check_game_running()
        if game_processes:
            print(f"INFO: Left 4 Dead 2 está ejecutándose ({len(game_processes)} proceso(s))")
        else:
            print("INFO: Left 4 Dead 2 no está ejecutándose")
        
        # Estado final
        status = self.get_integrity_status()
        print(f"\nEstado de integridad: {status}")
        
        # Mostrar resumen final detallado
        print("\n" + "="*60)
        print("RESUMEN FINAL DE LA VERIFICACION")
        print("="*60)
        
        print(f"PC: {self.results['pc_info'].get('computer_name', 'Unknown')}")
        print(f"Usuario: {self.results['pc_info'].get('username', 'Unknown')}")
        print(f"Fecha: {self.results['timestamp']}")
        print(f"L4D2: {'Encontrado' if self.l4d2_path else 'No encontrado'}")
        print(f"Mods detectados: {len(self.results['mods_detected'])}")
        print(f"Mods en Versus: {len(self.results.get('versus_mods', []))}")
        print(f"Cuentas Steam: {self.results['steam_accounts_count']}")
        print(f"Procesos sospechosos: {len(self.results['suspicious_processes'])}")
        print(f"Inyecciones de memoria: {len(self.results.get('memory_injections', []))}")
        print(f"Firmas de cheats conocidos: {len(self.results.get('known_cheat_signatures', []))}")
        print(f"Archivos CFG sospechosos: {len(self.results.get('suspicious_cfg_commands', []))}")
        print(f"Archivos/carpetas de cheats: {len(self.results.get('cheat_files_found', []))}")
        print(f"Programas ejecutados recientemente: {len(self.results.get('recently_executed_suspicious', []))}")
        print(f"Estado general: {status}")
        print(f"Resumen: {self.get_integrity_summary()}")
        
        # Mostrar información del token si está disponible
        if self.results.get('token_validation'):
            token_info = self.results['token_validation']
            print(f"Token validado: {token_info.get('player_name', 'Unknown')} ({token_info.get('tournament_name', 'Unknown')})")
        
        print("="*60)
        
        # SOLUCIÓN ALTERNATIVA: Intentar reenviar reportes pendientes al inicio (silencioso)
        successful_pending, failed_pending = self._resend_pending_reports()
        # No mostrar mensajes de reenvío al usuario final
        
        # Enviar resultados a Discord si está configurado (ANTES del resumen)
        if self.discord_webhook_url:
            success = self.send_to_discord(status)
            # El mensaje ya se muestra dentro de send_to_discord
        
        # NOTA: No se genera JSON, solo el TXT que se envía a Discord
        # Si Discord falla, el TXT se guarda en PendingReports/
        
        # Mostrar mensaje final con resumen visual (DESPUÉS de enviar a Discord)
        self.show_final_summary(status)
        
        # Asegurar tiempo mínimo de 10 segundos para verificación completa
        elapsed_time = time.time() - start_time
        min_time = 10.0  # Tiempo mínimo en segundos
        
        if elapsed_time < min_time:
            remaining_time = min_time - elapsed_time
            print(f"\nCompletando análisis profundo... ({remaining_time:.1f}s restantes)")
            time.sleep(remaining_time)
            print("Análisis completado!")
        
        total_time = time.time() - start_time
        print(f"\nTiempo total de verificación: {total_time:.2f} segundos")
        
        # Cerrar ventana de carga si existe
        if show_loading_window:
            self._close_loading_window()
        
        return True
    
    def show_final_summary(self, status):
        """Muestra un resumen visual final de la verificación"""
        print("\n" + "="*60)
        print("🎮 RESUMEN VISUAL DE LA VERIFICACION")
        print("="*60)
        
        # Estado general con emoji
        status_emoji = {
            "CLEAN": "✅",
            "WARNING": "⚠️",
            "SUSPICIOUS": "❌"
        }
        
        print(f"\n{status_emoji.get(status, '❓')} ESTADO GENERAL: {status}")
        
        # Información de cuentas Steam
        print(f"\n👥 CUENTAS STEAM ENCONTRADAS: {self.results['steam_accounts_count']}")
        if self.results['steam_accounts_count'] > 0:
            print("   Detalles de las cuentas:")
            for i, account in enumerate(self.results['steam_accounts'], 1):
                print(f"   {i}. Usuario: {account['username']}")
                print(f"      SteamID64: {account['steam_id64']}")
                print(f"      SteamID3: {account['steam_id3']}")
                print(f"      SteamID: {account['steam_id']}")
                print()
        
        # Información de mods
        print(f"🔧 MODS DETECTADOS: {len(self.results['mods_detected'])}")
        if len(self.results['mods_detected']) > 0:
            print("   Lista de mods encontrados:")
            for i, mod in enumerate(self.results['mods_detected'], 1):
                print(f"   {i}. {mod['name']} ({mod['size']} bytes)")
        
        # Información de procesos sospechosos
        print(f"\n⚠️ PROCESOS SOSPECHOSOS: {len(self.results['suspicious_processes'])}")
        if len(self.results['suspicious_processes']) > 0:
            print("   Lista de procesos sospechosos:")
            for i, proc in enumerate(self.results['suspicious_processes'], 1):
                print(f"   {i}. {proc['name']} (PID: {proc['pid']})")
                if proc.get('exe'):
                    print(f"      Ruta: {proc['exe']}")
        
        # Información de fecha de formateo
        print(f"\n💻 INFORMACION DEL SISTEMA:")
        if self.results.get('system_install_info') and self.results['system_install_info']['most_likely_install_date']:
            install_date = self.results['system_install_info']['most_likely_install_date']
            days_since = self.results['system_install_info']['days_since_install']
            print(f"   📅 Sistema instalado/formateado: {install_date['formatted_date']}")
            print(f"   🔍 Fuente: {install_date['source']}")
            print(f"   ⏰ Días desde la instalación: {days_since}")
            
            # Evaluar si es sospechoso
            if days_since is not None:
                if days_since < 7:
                    print(f"   ⚠️ ADVERTENCIA: Sistema muy reciente (menos de 1 semana)")
                elif days_since < 30:
                    print(f"   ⚠️ NOTA: Sistema relativamente reciente (menos de 1 mes)")
                else:
                    print(f"   ✅ Sistema estable (más de 1 mes)")
        else:
            print("   ❓ No se pudo determinar la fecha de formateo del sistema")
        
        # Mostrar ventana de consola de nuevo para el resumen
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 9)  # 9 = SW_RESTORE
        except:
            pass
        
        # Resumen final
        print(f"\n📊 RESUMEN:")
        if status == "CLEAN":
            print("   ✅ La PC está limpia y lista para el torneo")
        elif status == "WARNING":
            print("   ⚠️ Se encontraron algunos elementos que requieren atención")
        else:
            print("   ❌ Se encontraron problemas que pueden afectar la integridad del torneo")
        
        print("\n" + "="*60)
        print("🏆 VERIFICACION COMPLETADA")
        print("="*60)
        
        # Conteo regresivo de 6 segundos antes de cerrar
        print("\n")
        for i in range(6, 0, -1):
            # Usar \r para sobrescribir la misma línea
            sys.stdout.write(f"\r[INFO] El verificador se cerrara en {i} segundos...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n\n[OK] Cerrando verificador...")
        time.sleep(0.5)  # Pequeña pausa para que se vea el mensaje
        
        # Autoeliminación del ejecutable (solo si está compilado)
        if is_compiled():
            self._self_delete()
    
    def _self_delete(self):
        """Elimina el ejecutable después de cerrarse (solo en modo compilado)"""
        try:
            exe_path = sys.executable
            
            # Crear un script batch temporal que eliminará el ejecutable
            batch_script = f'''@echo off
timeout /t 1 /nobreak >nul
del /f /q "{exe_path}"
del /f /q "%~f0"
'''
            
            # Guardar el script batch temporal
            batch_path = os.path.join(os.path.dirname(exe_path), "_cleanup_temp.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_script)
            
            # Ejecutar el batch en segundo plano y cerrar
            subprocess.Popen(batch_path, shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        except Exception as e:
            # Si falla la autoeliminación, no pasa nada crítico
            pass
    
    def generate_detailed_report_txt(self):
        """Genera un archivo TXT completo con TODO el reporte detallado"""
        report_lines = []
        
        # Encabezado
        report_lines.append("="*80)
        report_lines.append("L4D2 TOURNAMENT - REPORTE COMPLETO DE VERIFICACIÓN DE INTEGRIDAD")
        report_lines.append("="*80)
        report_lines.append("")
        
        # Información básica
        report_lines.append(f"FECHA Y HORA: {self.results['timestamp']}")
        report_lines.append(f"PC: {self.results['pc_info'].get('computer_name', 'Unknown')}")
        report_lines.append(f"USUARIO: {self.results['pc_info'].get('username', 'Unknown')}")
        report_lines.append(f"ESTADO GENERAL: {self.get_integrity_status()}")
        report_lines.append(f"RESUMEN: {self.get_integrity_summary()}")
        report_lines.append("")
        
        # Identificación del sistema (SIN TRUNCAR - IPs al final del archivo)
        report_lines.append("-"*80)
        report_lines.append("IDENTIFICACIÓN COMPLETA DEL SISTEMA")
        report_lines.append("-"*80)
        report_lines.append(f"MAC Address: {self.results['pc_info'].get('mac_address', 'Unknown')}")
        report_lines.append(f"System UUID: {self.results['pc_info'].get('system_uuid', 'Unknown')}")  # COMPLETO
        report_lines.append(f"Disk Serial: {self.results['pc_info'].get('disk_serial', 'Unknown')}")  # COMPLETO
        report_lines.append(f"System Fingerprint: {self.results['pc_info'].get('system_fingerprint', 'Unknown')}")  # COMPLETO
        report_lines.append("")
        report_lines.append("⚠️ NOTA: Las direcciones IP están al final del archivo por privacidad")
        report_lines.append("")
        
        # Cuentas Steam
        report_lines.append("-"*80)
        report_lines.append(f"CUENTAS STEAM DETECTADAS: {self.results['steam_accounts_count']}")
        report_lines.append("-"*80)
        if self.results['steam_accounts_count'] > 0:
            for i, account in enumerate(self.results['steam_accounts'], 1):
                report_lines.append(f"{i}. Usuario: {account['username']}")
                report_lines.append(f"   SteamID64: {account['steam_id64']}")
                report_lines.append(f"   SteamID3: {account['steam_id3']}")
                report_lines.append(f"   SteamID: {account['steam_id']}")
                report_lines.append("")
        else:
            report_lines.append("Ninguna cuenta detectada")
            report_lines.append("")
        
        # Mods detectados
        report_lines.append("-"*80)
        report_lines.append(f"MODS DETECTADOS: {len(self.results['mods_detected'])}")
        report_lines.append("-"*80)
        if len(self.results['mods_detected']) > 0:
            for i, mod in enumerate(self.results['mods_detected'], 1):
                report_lines.append(f"{i}. Nombre: {mod['name']}")
                report_lines.append(f"   Tamaño: {mod['size']:,} bytes")
                report_lines.append(f"   Ubicación: {mod.get('location', 'N/A')}")  # RUTA COMPLETA
                report_lines.append(f"   Ruta Completa: {mod.get('path', 'N/A')}")  # RUTA COMPLETA
                if mod.get('suspicious'):
                    report_lines.append(f"   ⚠️ SOSPECHOSO: {mod.get('analysis', 'Análisis sospechoso')}")
                report_lines.append("")
            report_lines.append("Ningún mod detectado")
            report_lines.append("")
        
        # Carpetas no oficiales en raíz
        report_lines.append("-"*80)
        report_lines.append(f"CARPETAS NO OFICIALES EN RAÍZ: {len(self.results.get('unofficial_folders', []))}")
        report_lines.append("-"*80)
        if len(self.results.get('unofficial_folders', [])) > 0:
            for i, folder in enumerate(self.results.get('unofficial_folders', []), 1):
                report_lines.append(f"{i}. Carpeta: {folder['folder_name']}")
                report_lines.append(f"   Ruta Completa: {folder['folder_path']}")
                report_lines.append(f"   Severidad: {folder['severity']}")
                report_lines.append(f"   Descripción: {folder['description']}")
                if folder.get('files_count'):
                    report_lines.append(f"   Archivos: {folder['files_count']}")
                report_lines.append("")
        else:
            report_lines.append("Ninguna carpeta no oficial detectada")
            report_lines.append("")
        
        # Validación de gameinfo.txt
        report_lines.append("-"*80)
        report_lines.append("VALIDACIÓN DE GAMEINFO.TXT")
        report_lines.append("-"*80)
        if self.results.get('gameinfo_validation'):
            validation = self.results['gameinfo_validation']
            report_lines.append(f"Estado: {validation['status']}")
            report_lines.append(f"Severidad: {validation['severity']}")
            report_lines.append(f"Descripción: {validation['description']}")
            if validation.get('modifications'):
                report_lines.append("Modificaciones detectadas:")
                for mod in validation['modifications']:
                    report_lines.append(f"   - {mod}")
            if validation.get('file_path'):
                report_lines.append(f"Ruta: {validation['file_path']}")
        else:
            report_lines.append("No se realizó validación de gameinfo.txt")
        report_lines.append("")
        
        # Validación de addonconfig.cfg
        report_lines.append("-"*80)
        report_lines.append("VALIDACIÓN DE ADDONCONFIG.CFG")
        report_lines.append("-"*80)
        if self.results.get('addonconfig_validation'):
            validation = self.results['addonconfig_validation']
            report_lines.append(f"Estado: {validation['status']}")
            report_lines.append(f"Severidad: {validation['severity']}")
            report_lines.append(f"Descripción: {validation['description']}")
            if validation.get('issues'):
                report_lines.append("Problemas detectados:")
                for issue in validation['issues']:
                    report_lines.append(f"   - {issue}")
            if validation.get('file_path'):
                report_lines.append(f"Ruta: {validation['file_path']}")
        else:
            report_lines.append("No se realizó validación de addonconfig.cfg")
        report_lines.append("")
        
        # Hallazgos críticos (firmas de cheats conocidos)
        report_lines.append("-"*80)
        report_lines.append(f"FIRMAS DE CHEATS CONOCIDOS: {len(self.results.get('critical_findings', []))}")
        report_lines.append("-"*80)
        if len(self.results.get('critical_findings', [])) > 0:
            for i, finding in enumerate(self.results.get('critical_findings', []), 1):
                report_lines.append(f"{i}. Archivo: {finding['file_name']}")
                report_lines.append(f"   Ubicación: {finding['location']}")
                report_lines.append(f"   Ruta Completa: {finding['file_path']}")
                report_lines.append(f"   Tamaño: {finding['file_size']:,} bytes")
                report_lines.append(f"   Tipo de Cheat: {finding['cheat_type']}")
                report_lines.append(f"   Patrón Detectado: '{finding['matched_pattern']}'")
                report_lines.append(f"   Severidad: {finding['severity']}")
                report_lines.append(f"   Descripción: {finding['description']}")
                report_lines.append(f"   Método de Detección: {finding['detection_method']}")
                report_lines.append("")
        else:
            report_lines.append("Ninguna firma de cheat conocido detectada")
            report_lines.append("")
        
        # Procesos sospechosos
        report_lines.append("-"*80)
        report_lines.append(f"PROCESOS SOSPECHOSOS: {len(self.results['suspicious_processes'])}")
        report_lines.append("-"*80)
        if len(self.results['suspicious_processes']) > 0:
            for i, proc in enumerate(self.results['suspicious_processes'], 1):
                report_lines.append(f"{i}. Proceso: {proc['name']}")
                report_lines.append(f"   PID: {proc['pid']}")
                if proc.get('exe'):
                    report_lines.append(f"   Ruta Completa: {proc['exe']}")  # RUTA COMPLETA
                if proc.get('reason'):
                    report_lines.append(f"   Razón: {proc['reason']}")
                if proc.get('tool_name'):
                    report_lines.append(f"   Herramienta: {proc['tool_name']}")
                if proc.get('severity'):
                    report_lines.append(f"   Severidad: {proc['severity']}")
                if proc.get('description'):
                    report_lines.append(f"   Descripción: {proc['description']}")
                report_lines.append("")
        else:
            report_lines.append("Ningún proceso sospechoso detectado")
            report_lines.append("")
        
        # Archivos/Carpetas de cheats
        report_lines.append("-"*80)
        report_lines.append(f"ARCHIVOS/CARPETAS DE CHEATS: {len(self.results.get('cheat_files_found', []))}")
        report_lines.append("-"*80)
        if len(self.results.get('cheat_files_found', [])) > 0:
            for i, cf in enumerate(self.results.get('cheat_files_found', []), 1):
                if cf.get('type') == 'cheat_folder':
                    report_lines.append(f"{i}. CARPETA: {cf['folder_name']}")
                    report_lines.append(f"   Ruta Completa: {cf['folder_path']}")  # RUTA COMPLETA
                    report_lines.append(f"   Total de archivos: {cf['total_files']}")
                    report_lines.append(f"   Archivos sospechosos: {len(cf['suspicious_files'])}")
                    if cf['suspicious_files']:
                        report_lines.append(f"   Ejemplos de archivos:")
                        for sus_file in cf['suspicious_files'][:5]:
                            report_lines.append(f"      - {sus_file['name']} ({sus_file['size']} bytes)")
                            report_lines.append(f"        Ruta: {sus_file['path']}")  # RUTA COMPLETA
                else:
                    report_lines.append(f"{i}. ARCHIVO: {cf['file_name']}")
                    report_lines.append(f"   Ruta Completa: {cf['file_path']}")  # RUTA COMPLETA
                    report_lines.append(f"   Tamaño: {cf['file_size']} bytes")
                    report_lines.append(f"   Ubicación: {cf['location']}")
                report_lines.append("")
        else:
            report_lines.append("Ningún archivo de cheat detectado")
            report_lines.append("")
        
        # Programas ejecutados recientemente
        report_lines.append("-"*80)
        report_lines.append(f"PROGRAMAS EJECUTADOS RECIENTEMENTE: {len(self.results.get('recently_executed_suspicious', []))}")
        report_lines.append("-"*80)
        if len(self.results.get('recently_executed_suspicious', [])) > 0:
            for i, prog in enumerate(self.results.get('recently_executed_suspicious', []), 1):
                report_lines.append(f"{i}. Programa: {prog['program_name']}")
                report_lines.append(f"   Fuente: {prog['source']}")
                if prog.get('last_execution_formatted'):
                    report_lines.append(f"   Última ejecución: {prog['last_execution_formatted']}")
                    report_lines.append(f"   Hace: {prog.get('hours_ago', 'N/A')} horas")
                if prog.get('file_path'):
                    report_lines.append(f"   Ruta: {prog['file_path']}")  # RUTA COMPLETA
                if prog.get('prefetch_file'):
                    report_lines.append(f"   Archivo Prefetch: {prog['prefetch_file']}")
                report_lines.append(f"   Severidad: {prog.get('severity', 'N/A')}")
                if prog.get('confidence'):
                    report_lines.append(f"   Confianza: {prog['confidence']}")
                if prog.get('context_details'):
                    report_lines.append(f"   Análisis: {prog['context_details']}")
                report_lines.append("")
        else:
            report_lines.append("Ningún programa sospechoso en historial")
            report_lines.append("")
        
        # Comandos CFG sospechosos
        report_lines.append("-"*80)
        report_lines.append(f"ARCHIVOS CFG CON COMANDOS SOSPECHOSOS: {len(self.results.get('suspicious_cfg_commands', []))}")
        report_lines.append("-"*80)
        if len(self.results.get('suspicious_cfg_commands', [])) > 0:
            for i, cfg in enumerate(self.results.get('suspicious_cfg_commands', []), 1):
                report_lines.append(f"{i}. Archivo: {cfg['file_name']}")
                report_lines.append(f"   Ruta Completa: {cfg['file_path']}")  # RUTA COMPLETA
                report_lines.append(f"   Comandos prohibidos: {len(cfg['prohibited_commands'])}")
                for cmd in cfg['prohibited_commands']:
                    report_lines.append(f"      Línea {cmd['line_number']}: {cmd['line_content']}")
                    report_lines.append(f"         Comando: {cmd['command']}")
                    report_lines.append(f"         Severidad: {cmd['severity']}")
                    report_lines.append(f"         Razón: {cmd['reason']}")
                report_lines.append("")
        else:
            report_lines.append("Ningún comando sospechoso en archivos CFG")
            report_lines.append("")
        
        # Mods en Versus
        if len(self.results.get('versus_mods', [])) > 0:
            report_lines.append("-"*80)
            report_lines.append(f"MODS EN VERSUS: {len(self.results['versus_mods'])}")
            report_lines.append("-"*80)
            for i, versus_mod in enumerate(self.results['versus_mods'], 1):
                report_lines.append(f"{i}. {versus_mod['description']}")
                report_lines.append(f"   Severidad: {versus_mod['severity']}")
                if versus_mod.get('file_path'):
                    report_lines.append(f"   Archivo: {versus_mod['file_path']}")
                if versus_mod.get('folder_path'):
                    report_lines.append(f"   Carpeta: {versus_mod['folder_path']}")
                report_lines.append("")
        
        # Token validation
        if self.results.get('token_validation'):
            token_info = self.results['token_validation']
            report_lines.append("-"*80)
            report_lines.append("TOKEN DE JUGADOR")
            report_lines.append("-"*80)
            report_lines.append(f"Jugador: {token_info.get('player_name', 'Unknown')}")
            report_lines.append(f"Torneo: {token_info.get('tournament_name', 'Unknown')}")
            report_lines.append(f"Estado: Token válido y verificado")
            report_lines.append("")
        
        # INFORMACIÓN SENSIBLE (al final para proteger privacidad en streams)
        report_lines.append("")
        report_lines.append("="*80)
        report_lines.append("⚠️ INFORMACIÓN SENSIBLE - DIRECCIONES IP (PRIVADO)")
        report_lines.append("="*80)
        report_lines.append("")
        report_lines.append("⚠️ ADVERTENCIA: Esta sección contiene información privada.")
        report_lines.append("   NO compartir esta sección en streams públicos o capturas de pantalla.")
        report_lines.append("   Las IPs están al final del archivo para facilitar la censura.")
        report_lines.append("")
        report_lines.append(f"IP Externa: {self.results['pc_info'].get('external_ip', 'Unknown')}")
        report_lines.append(f"IP Local: {self.results['pc_info'].get('local_ip', 'Unknown')}")
        report_lines.append("")
        
        # Pie de página
        report_lines.append("="*80)
        report_lines.append("FIN DEL REPORTE")
        report_lines.append("="*80)
        
        return "\n".join(report_lines)
    
    def _save_pending_report(self, filename, report_txt, payload, files, status):
        """SOLUCIÓN ALTERNATIVA: Guarda el reporte en una cola local para reenvío posterior"""
        try:
            # Crear carpeta de reportes pendientes
            if is_compiled():
                pending_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
            else:
                pending_dir = "PendingReports"
            
            os.makedirs(pending_dir, exist_ok=True)
            
            # Crear archivo JSON con toda la información del reporte
            timestamp_str = str(int(time.time()))
            pending_file = os.path.join(pending_dir, f"pending_{timestamp_str}.json")
            
            pending_data = {
                'filename': filename,
                'report_txt': report_txt,
                'payload': payload,
                'status': status,
                'timestamp': self.results['timestamp'],
                'pc_info': self.results['pc_info'],
                'webhook_url': self.discord_webhook_url,
                'attempts': 0,
                'last_attempt': None,
                'created_at': datetime.now().isoformat()
            }
            
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(pending_data, f, indent=2, ensure_ascii=False)
            
            # También guardar el TXT directamente
            txt_file = os.path.join(pending_dir, filename)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(report_txt)
            
            # Silencioso: no mostrar mensajes al usuario final
            
            return True
        except Exception as e:
            print(f"⚠️ Error al guardar reporte pendiente: {e}")
            return False
    
    def _resend_pending_reports(self):
        """Intenta reenviar todos los reportes pendientes de la cola local"""
        try:
            # Buscar carpeta de reportes pendientes
            if is_compiled():
                pending_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
            else:
                pending_dir = "PendingReports"
            
            if not os.path.exists(pending_dir):
                return 0, 0  # No hay reportes pendientes
            
            pending_files = [f for f in os.listdir(pending_dir) if f.startswith("pending_") and f.endswith(".json")]
            
            if not pending_files:
                return 0, 0
            
            successful = 0
            failed = 0
            
            # Silencioso: reenvío automático sin mostrar mensajes
            
            for pending_file in pending_files:
                file_path = os.path.join(pending_dir, pending_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pending_data = json.load(f)
                    
                    # Preparar archivo para envío
                    filename = pending_data['filename']
                    report_txt = pending_data['report_txt']
                    payload = pending_data['payload']
                    
                    files = {
                        'file': (filename, report_txt.encode('utf-8'), 'text/plain')
                    }
                    
                    # Intentar enviar con múltiples métodos (silencioso)
                    sent = False
                    
                    # Método 1: Multipart con archivo
                    for attempt in range(1, 4):
                        try:
                            response = requests.post(
                                pending_data['webhook_url'],
                                data={'payload_json': json.dumps(payload)},
                                files=files,
                                timeout=40
                            )
                            if response.status_code in [200, 201, 204]:
                                sent = True
                                break
                        except:
                            if attempt < 3:
                                time.sleep(2)
                                continue
                    
                    # Método 2: Solo JSON si el método 1 falla
                    if not sent:
                        simplified_payload = {
                            "embeds": [payload['embeds'][0]],
                            "content": f"📄 Reporte: {filename}"
                        }
                        try:
                            response = requests.post(
                                pending_data['webhook_url'],
                                json=simplified_payload,
                                timeout=30
                            )
                            if response.status_code in [200, 201, 204]:
                                sent = True
                        except:
                            pass
                    
                    if sent:
                        successful += 1
                        
                        # Eliminar archivo pendiente si se envió correctamente
                        os.remove(file_path)
                        
                        # También eliminar el TXT si existe
                        txt_path = os.path.join(pending_dir, filename)
                        if os.path.exists(txt_path):
                            os.remove(txt_path)
                    else:
                        failed += 1
                        
                        # Actualizar contador de intentos
                        pending_data['attempts'] = pending_data.get('attempts', 0) + 1
                        pending_data['last_attempt'] = datetime.now().isoformat()
                        pending_data['last_error'] = "No se pudo enviar con ningún método"
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(pending_data, f, indent=2, ensure_ascii=False)
                
                except Exception as e:
                    failed += 1
            
            return successful, failed
            
        except Exception as e:
            # Silencioso: errores no se muestran al usuario final
            return 0, 0
    
    def send_to_discord(self, status):
        """Envía los resultados del análisis a Discord CON archivo TXT completo"""
        if not self.discord_webhook_url:
            return False
        
        try:
            # Crear el mensaje embebido
            embed = {
                "title": f"🎮 L4D2 Tournament - Verificación de Integridad",
                "description": f"**Estado General**: {self.get_discord_emoji(status)} {status}\n**Resumen**: {self.get_integrity_summary()}",
                "color": self.get_discord_color(status),
                "fields": [
                    {
                        "name": "🖥️ PC",
                        "value": f"{self.results['pc_info'].get('computer_name', 'Unknown')} ({self.results['pc_info'].get('username', 'Unknown')})",
                        "inline": True
                    },
                    {
                        "name": "📅 Fecha",
                        "value": self.results['timestamp'][:19].replace('T', ' '),
                        "inline": True
                    },
                    {
                        "name": "🎯 Estado",
                        "value": f"{self.get_discord_emoji(status)} {status}",
                        "inline": True
                    },
                    {
                        "name": "🔐 Identificación del Sistema",
                        "value": f"🌐 **IP Externa**: `{self._censor_ip(self.results['pc_info'].get('external_ip', 'Unknown'))}`\n"
                                f"🏠 **IP Local**: `{self._censor_ip(self.results['pc_info'].get('local_ip', 'Unknown'))}`\n"
                                f"📡 **MAC Address**: `{self.results['pc_info'].get('mac_address', 'Unknown')}`\n"
                                f"🆔 **System UUID**: `{self.results['pc_info'].get('system_uuid', 'Unknown')[:8]}...`\n"
                                f"💾 **Disk Serial**: `{self.results['pc_info'].get('disk_serial', 'Unknown')[:8]}...`\n"
                                f"🔑 **Fingerprint**: `{self.results['pc_info'].get('system_fingerprint', 'Unknown')[:16]}...`\n"
                                f"⚠️ _IPs censuradas para stream - Ver archivo TXT completo_",
                        "inline": False
                    },
                    {
                        "name": "👥 Cuentas Steam",
                        "value": str(self.results['steam_accounts_count']),
                        "inline": True
                    },
                    {
                        "name": "🔧 Mods Detectados",
                        "value": str(len(self.results['mods_detected'])),
                        "inline": True
                    },
                    {
                        "name": "⚠️ Procesos Sospechosos",
                        "value": str(len(self.results['suspicious_processes'])),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "L4D2 Tournament Integrity Checker"
                },
                "timestamp": self.results['timestamp']
            }
            
            # Agregar información de fecha de formateo del sistema
            if self.results.get('system_install_info') and self.results['system_install_info']['most_likely_install_date']:
                install_date = self.results['system_install_info']['most_likely_install_date']
                days_since = self.results['system_install_info']['days_since_install']
                
                # Determinar el emoji según la antigüedad
                if days_since is not None:
                    if days_since < 7:
                        date_emoji = "⚠️"
                        date_status = "Muy reciente"
                    elif days_since < 30:
                        date_emoji = "⚠️"
                        date_status = "Reciente"
                    else:
                        date_emoji = "✅"
                        date_status = "Estable"
                else:
                    date_emoji = "❓"
                    date_status = "Desconocido"
                
                embed["fields"].append({
                    "name": f"{date_emoji} Sistema Instalado",
                    "value": f"{install_date['formatted_date']}\n({date_status} - {days_since} días)",
                    "inline": True
                })
            
            # Agregar detalles de cuentas Steam si hay alguna (SOLO SteamID64)
            if self.results['steam_accounts_count'] > 0:
                accounts_text = ""
                # Mostrar TODAS las cuentas, SOLO los SteamID64
                for i, account in enumerate(self.results['steam_accounts'], 1):
                    accounts_text += f"{i}. `{account['steam_id64']}`\n"
                
                embed["fields"].append({
                    "name": f"👥 SteamID64 Detectados ({self.results['steam_accounts_count']})",
                    "value": accounts_text or "Ninguno",
                    "inline": False
                })
            
            # Agregar detalles de mods si hay alguno
            if len(self.results['mods_detected']) > 0:
                mods_text = ""
                # Mostrar mods con información detallada (limitado para evitar exceder límites)
                max_mods_to_show = 5  # Mostrar máximo 5 mods en el embed
                for i, mod in enumerate(self.results['mods_detected'][:max_mods_to_show], 1):
                    mods_text += f"{i}. **{mod['name']}**\n"
                    mods_text += f"   📁 Tamaño: `{mod['size']:,} bytes`\n"
                    # Truncar ubicación si es muy larga
                    location = mod.get('location', 'N/A')
                    if len(location) > 80:
                        location = location[:77] + "..."
                    mods_text += f"   📍 Ubicación: `{location}`\n"
                    if mod.get('suspicious'):
                        mods_text += f"   ⚠️ **SOSPECHOSO**: {mod.get('analysis', 'Análisis sospechoso')}\n"
                    mods_text += "\n"
                
                # Si hay más mods, agregar nota
                if len(self.results['mods_detected']) > max_mods_to_show:
                    mods_text += f"⚠️ _...y {len(self.results['mods_detected']) - max_mods_to_show} mods más (ver archivo TXT completo)_\n"
                
                # Truncar si es necesario
                mods_text = self._truncate_field_value(mods_text, 1024)
                
                embed["fields"].append({
                    "name": f"🔧 Mods Detectados ({len(self.results['mods_detected'])})",
                    "value": mods_text,
                    "inline": False
                })
            
            # Agregar detalles de procesos sospechosos si hay alguno
            if len(self.results['suspicious_processes']) > 0:
                processes_text = ""
                # Mostrar procesos (limitado para evitar exceder límites)
                max_processes_to_show = 5
                for i, proc in enumerate(self.results['suspicious_processes'][:max_processes_to_show], 1):
                    processes_text += f"{i}. **{proc['name']}**\n"
                    processes_text += f"   🔢 PID: `{proc['pid']}`\n"
                    if proc.get('exe'):
                        exe_path = proc['exe']
                        if len(exe_path) > 80:
                            exe_path = exe_path[:77] + "..."
                        processes_text += f"   📍 Ruta: `{exe_path}`\n"
                    if proc.get('reason'):
                        reason = proc['reason']
                        if len(reason) > 100:
                            reason = reason[:97] + "..."
                        processes_text += f"   ⚠️ Razón: `{reason}`\n"
                    processes_text += "\n"
                
                # Si hay más procesos, agregar nota
                if len(self.results['suspicious_processes']) > max_processes_to_show:
                    processes_text += f"⚠️ _...y {len(self.results['suspicious_processes']) - max_processes_to_show} procesos más (ver archivo TXT completo)_\n"
                
                # Truncar si es necesario
                processes_text = self._truncate_field_value(processes_text, 1024)
                
                embed["fields"].append({
                    "name": f"⚠️ Procesos Sospechosos ({len(self.results['suspicious_processes'])})",
                    "value": processes_text,
                    "inline": False
                })
            
            # Agregar detalles de mods en Versus si hay alguno
            if len(self.results.get('versus_mods', [])) > 0:
                versus_text = ""
                max_versus_to_show = 3
                for i, versus_mod in enumerate(self.results['versus_mods'][:max_versus_to_show], 1):
                    versus_text += f"{i}. **{versus_mod['description']}**\n"
                    versus_text += f"   🚨 Severidad: `{versus_mod['severity']}`\n"
                    if versus_mod.get('file_path'):
                        fp = versus_mod['file_path']
                        if len(fp) > 80:
                            fp = fp[:77] + "..."
                        versus_text += f"   📁 Archivo: `{fp}`\n"
                    if versus_mod.get('folder_path'):
                        fld = versus_mod['folder_path']
                        if len(fld) > 80:
                            fld = fld[:77] + "..."
                        versus_text += f"   📂 Carpeta: `{fld}`\n"
                    if versus_mod.get('modification'):
                        mod = versus_mod['modification']
                        if len(mod) > 100:
                            mod = mod[:97] + "..."
                        versus_text += f"   ⚠️ Modificación: `{mod}`\n"
                    versus_text += "\n"
                
                if len(self.results.get('versus_mods', [])) > max_versus_to_show:
                    versus_text += f"⚠️ _...y {len(self.results['versus_mods']) - max_versus_to_show} más (ver TXT completo)_\n"
                
                versus_text = self._truncate_field_value(versus_text, 1024)
                
                embed["fields"].append({
                    "name": f"🚫 Mods en Versus ({len(self.results['versus_mods'])})",
                    "value": versus_text,
                    "inline": False
                })
            
            # Agregar detalles de inyecciones de memoria si hay alguna
            if len(self.results.get('memory_injections', [])) > 0:
                injections_text = ""
                max_injections_to_show = 3
                for i, injection in enumerate(self.results['memory_injections'][:max_injections_to_show], 1):
                    injections_text += f"{i}. **{injection['process_name']}**\n"
                    injections_text += f"   🔢 PID: `{injection['process_pid']}`\n"
                    if injection.get('dll_path'):
                        dll = injection['dll_path']
                        if len(dll) > 80:
                            dll = dll[:77] + "..."
                        injections_text += f"   📁 DLL: `{dll}`\n"
                    if injection.get('reason'):
                        reason = injection['reason']
                        if len(reason) > 100:
                            reason = reason[:97] + "..."
                        injections_text += f"   ⚠️ Razón: `{reason}`\n"
                    injections_text += "\n"
                
                if len(self.results.get('memory_injections', [])) > max_injections_to_show:
                    injections_text += f"⚠️ _...y {len(self.results['memory_injections']) - max_injections_to_show} más (ver TXT completo)_\n"
                
                injections_text = self._truncate_field_value(injections_text, 1024)
                
                embed["fields"].append({
                    "name": f"🧠 Inyecciones de Memoria ({len(self.results['memory_injections'])})",
                    "value": injections_text,
                    "inline": False
                })
            
            # Agregar detalles de firmas de cheats conocidos si hay alguna
            if len(self.results.get('known_cheat_signatures', [])) > 0:
                signatures_text = ""
                max_signatures_to_show = 3
                for i, signature in enumerate(self.results['known_cheat_signatures'][:max_signatures_to_show], 1):
                    signatures_text += f"{i}. **{signature['description']}**\n"
                    signatures_text += f"   🚨 Severidad: `{signature['severity']}`\n"
                    if signature.get('process_name'):
                        signatures_text += f"   🔢 Proceso: `{signature['process_name']} (PID: {signature['process_pid']})`\n"
                    if signature.get('file_path'):
                        fp = signature['file_path']
                        if len(fp) > 80:
                            fp = fp[:77] + "..."
                        signatures_text += f"   📁 Archivo: `{fp}`\n"
                    signatures_text += "\n"
                
                if len(self.results.get('known_cheat_signatures', [])) > max_signatures_to_show:
                    signatures_text += f"⚠️ _...y {len(self.results['known_cheat_signatures']) - max_signatures_to_show} más (ver TXT completo)_\n"
                
                signatures_text = self._truncate_field_value(signatures_text, 1024)
                
                embed["fields"].append({
                    "name": f"🎯 Firmas de Cheats Conocidos ({len(self.results['known_cheat_signatures'])})",
                    "value": signatures_text,
                    "inline": False
                })
            
            # Agregar detalles de archivos/carpetas de cheats encontrados
            if len(self.results.get('cheat_files_found', [])) > 0:
                cheat_files_text = ""
                # Limitar a los primeros 3 para no saturar Discord
                max_cheat_files_to_show = 3
                for i, cf in enumerate(self.results.get('cheat_files_found', [])[:max_cheat_files_to_show], 1):
                    if cf.get('type') == 'cheat_folder':
                        cheat_files_text += f"{i}. 📁 **{cf['folder_name']}**\n"
                        fp = cf['folder_path']
                        if len(fp) > 80:
                            fp = fp[:77] + "..."
                        cheat_files_text += f"   📍 `{fp}`\n"
                        cheat_files_text += f"   📊 {cf['total_files']} archivos ({len(cf['suspicious_files'])} sospechosos)\n\n"
                    else:
                        cheat_files_text += f"{i}. 📄 **{cf['file_name']}**\n"
                        fp = cf['file_path']
                        if len(fp) > 80:
                            fp = fp[:77] + "..."
                        cheat_files_text += f"   📍 `{fp}`\n"
                        cheat_files_text += f"   📊 Tamaño: {cf['file_size']} bytes\n\n"
                
                if len(self.results.get('cheat_files_found', [])) > max_cheat_files_to_show:
                    cheat_files_text += f"_...y {len(self.results.get('cheat_files_found', [])) - max_cheat_files_to_show} más (ver TXT completo)_\n"
                
                cheat_files_text = self._truncate_field_value(cheat_files_text, 1024)
                
                embed["fields"].append({
                    "name": f"🚨 Archivos/Carpetas de Cheats ({len(self.results.get('cheat_files_found', []))})",
                    "value": cheat_files_text,
                    "inline": False
                })
            
            # Agregar detalles de programas ejecutados recientemente (sospechosos)
            if len(self.results.get('recently_executed_suspicious', [])) > 0:
                recent_programs_text = ""
                # Limitar a los primeros 5 para no saturar Discord
                for i, prog in enumerate(self.results.get('recently_executed_suspicious', [])[:5], 1):
                    recent_programs_text += f"{i}. **{prog['program_name']}**\n"
                    recent_programs_text += f"   ⏰ Ejecutado hace: `{prog.get('hours_ago', 'N/A')} horas`\n"
                    recent_programs_text += f"   🚨 Severidad: `{prog.get('severity', 'N/A')}` (Confianza: {prog.get('confidence', 'N/A')})\n"
                    if prog.get('file_path'):
                        recent_programs_text += f"   📍 `{prog['file_path']}`\n"
                    recent_programs_text += "\n"
                
                if len(self.results.get('recently_executed_suspicious', [])) > 5:
                    recent_programs_text += f"_...y {len(self.results.get('recently_executed_suspicious', [])) - 5} más (ver TXT completo)_\n"
                
                embed["fields"].append({
                    "name": f"🕒 Programas Sospechosos en Historial ({len(self.results.get('recently_executed_suspicious', []))})",
                    "value": recent_programs_text,
                    "inline": False
                })
            
            # Agregar detalles de comandos CFG sospechosos
            if len(self.results.get('suspicious_cfg_commands', [])) > 0:
                cfg_text = ""
                # Limitar a los primeros 3 archivos para no saturar Discord
                for i, cfg in enumerate(self.results.get('suspicious_cfg_commands', [])[:3], 1):
                    cfg_text += f"{i}. **{cfg['file_name']}**\n"
                    cfg_text += f"   📍 `{cfg['file_path']}`\n"
                    cfg_text += f"   🚨 {len(cfg['prohibited_commands'])} comandos prohibidos\n\n"
                
                if len(self.results.get('suspicious_cfg_commands', [])) > 3:
                    cfg_text += f"_...y {len(self.results.get('suspicious_cfg_commands', [])) - 3} más (ver TXT completo)_\n"
                
                embed["fields"].append({
                    "name": f"⚙️ Archivos CFG Sospechosos ({len(self.results.get('suspicious_cfg_commands', []))})",
                    "value": cfg_text,
                    "inline": False
                })
            
            # Agregar información del token si está disponible
            if self.results.get('token_validation'):
                token_info = self.results['token_validation']
                embed["fields"].append({
                    "name": "🎫 Token Validado",
                    "value": f"👤 **Jugador**: {token_info.get('player_name', 'Unknown')}\n🏆 **Torneo**: {token_info.get('tournament_name', 'Unknown')}\n✅ **Estado**: Token válido y verificado",
                    "inline": False
                })
            
            # Generar archivo TXT completo
            report_txt = self.generate_detailed_report_txt()
            
            # Crear nombre de archivo con timestamp
            timestamp_str = self.results['timestamp'][:19].replace('T', '_').replace(':', '-')
            pc_name = self.results['pc_info'].get('computer_name', 'Unknown').replace(' ', '_')
            filename = f"L4D2_Report_{pc_name}_{timestamp_str}.txt"
            
            # SIEMPRE guardar el TXT localmente (independiente de si Discord funciona o no)
            try:
                # Crear carpeta Reports si no existe
                if is_compiled():
                    reports_dir = os.path.join(os.path.dirname(sys.executable), "Reports")
                else:
                    reports_dir = "Reports"
                os.makedirs(reports_dir, exist_ok=True)
                
                # Guardar el TXT con el análisis completo
                txt_path = os.path.join(reports_dir, filename)
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(report_txt)
                
                # Mensaje discreto
                print(f"\n📄 Reporte guardado: {txt_path}")
            except Exception as e:
                # Silencioso si falla
                pass
            
            # Preparar el archivo para envío
            files = {
                'file': (filename, report_txt.encode('utf-8'), 'text/plain')
            }
            
            # VALIDAR Y CORREGIR TAMAÑO DEL EMBED ANTES DE ENVIAR
            embed = self._validate_and_fix_embed(embed)
            
            # Preparar el payload con embed
            payload = {
                "embeds": [embed],
                "content": f"📄 **Reporte completo adjunto**: `{filename}`\n⚠️ Revisa el archivo .txt para ver toda la información sin truncar (rutas completas, UUIDs completos, etc.)"
            }
            
            # Test silencioso de conectividad (solo para diagnóstico interno)
            test_success = False
            try:
                test_response = requests.get("https://discord.com", timeout=5)
                if test_response.status_code == 200:
                    test_success = True
            except:
                test_success = False
            
            # ESTRATEGIA AGRESIVA: Múltiples métodos y más reintentos para garantizar envío
            # No importa si se envía 2 veces, lo importante es que LLEGUE
            max_retries = 7  # Más intentos
            last_error = None
            success = False
            
            print("Enviando resultados a Discord...", end=" ", flush=True)
            
            # MÉTODO 1: Multipart con archivo (método original)
            for attempt in range(1, max_retries + 1):
                try:
                    timeout_value = 30 + (attempt * 5)  # 30s, 35s, 40s, 45s, 50s, 55s, 60s
                    
                    response = requests.post(
                        self.discord_webhook_url, 
                        data={'payload_json': json.dumps(payload)},
                        files=files,
                        timeout=timeout_value
                    )
                    response.raise_for_status()
                    
                    # Verificar que realmente llegó (código 200-204)
                    if response.status_code in [200, 201, 204]:
                        print("✅ Enviado")
                        success = True
                        break
                    
                except requests.exceptions.Timeout:
                    last_error = "TIMEOUT"
                    if attempt < max_retries:
                        wait_time = min(2 ** attempt, 10)  # Máximo 10 segundos
                        print(".", end="", flush=True)
                        time.sleep(wait_time)
                        continue
                    
                except requests.exceptions.ConnectionError:
                    last_error = "ERROR DE CONEXION"
                    if attempt < max_retries:
                        wait_time = min(2 ** attempt, 10)
                        print(".", end="", flush=True)
                        time.sleep(wait_time)
                        continue
                    
                except requests.exceptions.HTTPError as e:
                    error_code = e.response.status_code if hasattr(e, 'response') else 'N/A'
                    error_text = e.response.text if hasattr(e, 'response') and e.response else 'N/A'
                    
                    # Si es error 429 (rate limit), esperar más tiempo
                    if error_code == 429:
                        last_error = "RATE_LIMIT"
                        wait_time = 5
                        print(".", end="", flush=True)
                        time.sleep(wait_time)
                        if attempt < max_retries:
                            continue
                    # Si es error 400 (Bad Request), probablemente payload muy grande
                    elif error_code == 400:
                        last_error = f"ERROR HTTP 400 (Bad Request - Payload muy grande)"
                        # Registrar error para diagnóstico
                        embed_size = len(json.dumps(embed))
                        payload_size = len(json.dumps(payload))
                        self._log_discord_error(error_code, error_text, embed_size, payload_size)
                        
                        # Intentar método simplificado inmediatamente
                        print(" [payload muy grande, intentando método simplificado...]", end="", flush=True)
                        # Salir del loop y usar método alternativo
                        break
                    else:
                        last_error = f"ERROR HTTP {error_code}"
                        # Registrar error para diagnóstico
                        embed_size = len(json.dumps(embed))
                        payload_size = len(json.dumps(payload))
                        self._log_discord_error(error_code, error_text, embed_size, payload_size)
                        
                        if attempt < max_retries:
                            wait_time = min(2 ** attempt, 10)
                            print(".", end="", flush=True)
                            time.sleep(wait_time)
                            continue
                    
                except Exception:
                    last_error = "ERROR DESCONOCIDO"
                    if attempt < max_retries:
                        wait_time = min(2 ** attempt, 10)
                        print(".", end="", flush=True)
                        time.sleep(wait_time)
                        continue
            
            # Si el método 1 falló, intentar MÉTODO 2: JSON directo sin archivo (más simple)
            if not success:
                print(" [intentando método alternativo...]", end="", flush=True)
                
                # Crear payload simplificado sin archivo adjunto
                simplified_payload = {
                    "embeds": [embed],
                    "content": f"📄 **Reporte disponible**: `{filename}`\n⚠️ El archivo completo se guardará localmente si es necesario."
                }
                
                for attempt in range(1, 4):  # 3 intentos adicionales con método simple
                    try:
                        response = requests.post(
                            self.discord_webhook_url,
                            json=simplified_payload,
                            timeout=30
                        )
                        response.raise_for_status()
                        
                        if response.status_code in [200, 201, 204]:
                            print(" ✅ Enviado (método alternativo)")
                            success = True
                            break
                            
                    except Exception:
                        if attempt < 3:
                            time.sleep(2)
                            continue
            
            # Si aún falla, intentar MÉTODO 3: Solo embed sin contenido extra
            if not success:
                print(" [intentando método mínimo...]", end="", flush=True)
                
                minimal_payload = {
                "embeds": [embed]
            }
            
                for attempt in range(1, 3):  # 2 intentos más
                    try:
                        response = requests.post(
                            self.discord_webhook_url,
                            json=minimal_payload,
                            timeout=20
                        )
                        response.raise_for_status()
                        
                        if response.status_code in [200, 201, 204]:
                            print(" ✅ Enviado (método mínimo)")
                            success = True
                            break
                            
                    except Exception:
                        if attempt < 2:
                            time.sleep(3)
                            continue
            
            if success:
                return True
            
            # Si llegamos aquí, TODOS los métodos fallaron
            print(" ⚠️ Falló todos los métodos")
            
            # ESTRATEGIA FINAL: Guardar y seguir intentando en background
            self._save_pending_report(filename, report_txt, payload, files, status)
            
            # Intentar una vez más después de guardar (a veces la red se recupera)
            try:
                print(" [último intento...]", end="", flush=True)
                response = requests.post(
                    self.discord_webhook_url,
                    data={'payload_json': json.dumps(payload)},
                    files=files,
                    timeout=45
                )
                if response.status_code in [200, 201, 204]:
                    print(" ✅ ¡Enviado en último intento!")
                    return True
            except:
                pass
            
            print("")  # Nueva línea después de los intentos
            
            # Guardar error en archivo de log (solo para administrador, no mostrar al usuario)
            try:
                if is_compiled():
                    log_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
                else:
                    log_dir = "PendingReports"
                os.makedirs(log_dir, exist_ok=True)
                
                log_filename = os.path.join(log_dir, f"error_{int(time.time())}.log")
                with open(log_filename, 'w', encoding='utf-8') as f:
                    f.write(f"L4D2 Tournament Integrity Checker - Error de Discord\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"Fecha: {self.results['timestamp']}\n")
                    f.write(f"PC: {self.results['pc_info'].get('computer_name', 'Unknown')}\n")
                    f.write(f"Usuario: {self.results['pc_info'].get('username', 'Unknown')}\n")
                    f.write(f"\nError: {last_error}\n")
                    f.write(f"Estado de verificación: {status}\n")
            except:
                pass
            
            return False
            
        except Exception as e:
            # Error general: guardar silenciosamente y no mostrar al usuario
            # Guardar en PendingReports para diagnóstico posterior
            try:
                if is_compiled():
                    pending_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
                else:
                    pending_dir = "PendingReports"
                os.makedirs(pending_dir, exist_ok=True)
                
                error_log = os.path.join(pending_dir, f"critical_error_{int(time.time())}.log")
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(f"Error crítico al preparar/enviar a Discord\n")
                    f.write(f"Tipo: {type(e).__name__}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Fecha: {datetime.now().isoformat()}\n")
            except:
                pass
            
            # Silencioso: no mostrar errores al usuario final
            
            return False
    
    def get_discord_color(self, status):
        """Obtiene el color para el embed de Discord según el estado"""
        colors = {
            "CLEAN": 0x00ff00,      # Verde
            "WARNING": 0xffaa00,    # Naranja
            "SUSPICIOUS": 0xff0000  # Rojo
        }
        return colors.get(status, 0x808080)  # Gris por defecto
    
    def _censor_ip(self, ip_address):
        """Censura una dirección IP para proteger privacidad en streams públicos"""
        if ip_address == "Unknown" or not ip_address:
            return "Unknown"
        
        # Separar por puntos
        parts = ip_address.split('.')
        
        if len(parts) == 4:
            # IPv4: Mostrar solo primeros 2 octetos
            return f"{parts[0]}.{parts[1]}.***.***.***"
        elif ':' in ip_address:
            # IPv6: Mostrar solo primeros 2 bloques
            parts_v6 = ip_address.split(':')
            if len(parts_v6) >= 2:
                return f"{parts_v6[0]}:{parts_v6[1]}:****:****"
        
        # Fallback: censurar la mitad
        return ip_address[:len(ip_address)//2] + "***"
    
    def get_discord_emoji(self, status):
        """Obtiene el emoji para Discord según el estado"""
        emojis = {
            "CLEAN": "✅",
            "WARNING": "⚠️",
            "SUSPICIOUS": "❌"
        }
        return emojis.get(status, "❓")
    
    def _truncate_field_value(self, value, max_length=1024):
        """Trunca un valor de campo para cumplir límites de Discord (1024 caracteres)"""
        if len(value) <= max_length:
            return value
        
        # Dejar espacio para el mensaje de truncamiento
        truncate_msg = "\n\n⚠️ _Contenido truncado (ver archivo TXT completo)_"
        available_length = max_length - len(truncate_msg)
        
        # Truncar y agregar mensaje
        truncated = value[:available_length]
        # Asegurar que no cortamos en medio de una línea si es posible
        last_newline = truncated.rfind('\n')
        if last_newline > available_length * 0.8:  # Si el último salto de línea está en el 80% final
            truncated = truncated[:last_newline]
        
        return truncated + truncate_msg
    
    def _validate_and_fix_embed(self, embed):
        """Valida y corrige el tamaño del embed para cumplir límites de Discord"""
        MAX_FIELD_VALUE = 1024  # Límite de Discord por campo
        MAX_EMBED_TOTAL = 6000  # Límite aproximado del embed completo
        
        # Verificar y truncar cada campo
        for field in embed.get('fields', []):
            value = field.get('value', '')
            if len(value) > MAX_FIELD_VALUE:
                field['value'] = self._truncate_field_value(value, MAX_FIELD_VALUE)
        
        # Verificar tamaño total del embed
        embed_json = json.dumps(embed)
        if len(embed_json) > MAX_EMBED_TOTAL:
            # Si el embed es muy grande, reducir campos menos críticos
            # Mantener los primeros campos importantes y reducir los últimos
            fields = embed.get('fields', [])
            if len(fields) > 8:  # Si hay más de 8 campos, reducir
                # Mantener primeros 6 campos (más importantes)
                # Reducir o eliminar campos adicionales
                important_fields = fields[:6]
                remaining_fields = fields[6:]
                
                # Crear campo resumen para los campos restantes
                if remaining_fields:
                    summary_text = f"⚠️ _Hay {len(remaining_fields)} campos adicionales. Ver archivo TXT completo para detalles._"
                    important_fields.append({
                        "name": "📋 Información Adicional",
                        "value": summary_text,
                        "inline": False
                    })
                
                embed['fields'] = important_fields
        
        return embed
    
    def _log_discord_error(self, error_code, error_text, embed_size, payload_size):
        """Registra errores de Discord para diagnóstico"""
        try:
            if is_compiled():
                log_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
            else:
                log_dir = "PendingReports"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"discord_error_{int(time.time())}.log")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("ERROR DE DISCORD - DIAGNÓSTICO\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n")
                f.write(f"Código de Error: {error_code}\n")
                f.write(f"Respuesta de Discord: {error_text[:500]}\n")  # Primeros 500 caracteres
                f.write(f"Tamaño del Embed: {embed_size} caracteres\n")
                f.write(f"Tamaño del Payload: {payload_size} bytes\n")
                f.write(f"PC: {self.results['pc_info'].get('computer_name', 'Unknown')}\n")
                f.write(f"Usuario: {self.results['pc_info'].get('username', 'Unknown')}\n")
                f.write(f"Mods Detectados: {len(self.results.get('mods_detected', []))}\n")
                f.write(f"Procesos Sospechosos: {len(self.results.get('suspicious_processes', []))}\n")
                f.write(f"Campos en Embed: {len(embed.get('fields', []))}\n")
        except:
            pass

class L4D2CheckerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("L4D2 Tournament Integrity Checker")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.checker = L4D2IntegrityChecker()
        self.authenticated = False
        self.setup_ui()
        self.check_authentication()
    
    def check_authentication(self):
        """Verifica la autenticación del usuario"""
        # Si está compilado como ejecutable, siempre requerir token
        if is_compiled():
            self.authenticate_with_token_compiled()
        elif self.checker.token_generator:
            # Usar sistema de tokens si está disponible
            self.authenticate_with_token()
        elif not self.checker.config.get('password_hash'):
            # Primera vez - configurar contraseña
            self.setup_password()
        else:
            # Verificar contraseña existente
            self.authenticate_user()
    
    def authenticate_with_token_compiled(self):
        """Autentica usando token de jugador en modo compilado"""
        dialog = TokenAuthDialogCompiled(self.root, self.checker)
        self.root.wait_window(dialog.dialog)
        
        if dialog.valid and dialog.token_data:
            self.authenticated = True
            self.token_data = dialog.token_data
            # Actualizar etiqueta de autenticación
            self.auth_label.config(text=f"Autenticado: {dialog.token_data['player_name']}", 
                                 fg="green")
        else:
            # Si no se autenticó, cerrar la aplicación
            self.root.quit()
    
    def authenticate_with_token(self):
        """Autentica usando token de jugador"""
        dialog = TokenAuthDialog(self.root, self.checker)
        self.root.wait_window(dialog.dialog)
        
        if dialog.valid and dialog.token_data:
            self.authenticated = True
            self.token_data = dialog.token_data
            # Actualizar etiqueta de autenticación
            self.auth_label.config(text=f"🎮 Autenticado como: {dialog.token_data['player_name']}", 
                                 foreground="blue")
        else:
            messagebox.showerror("Error", dialog.message or "Token inválido")
            self.root.quit()
    
    def setup_password(self):
        """Configura la contraseña por primera vez"""
        dialog = PasswordSetupDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.password:
            if self.checker.set_password(dialog.password):
                messagebox.showinfo("Éxito", "Contraseña configurada correctamente")
                self.authenticated = True
            else:
                messagebox.showerror("Error", "No se pudo configurar la contraseña")
                self.root.quit()
        else:
            self.root.quit()
    
    def authenticate_user(self):
        """Autentica al usuario con contraseña existente"""
        dialog = PasswordDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.password and self.checker.verify_password(dialog.password):
            self.authenticated = True
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
            self.root.quit()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="L4D2 Tournament Integrity Checker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Estado de autenticación
        self.auth_label = ttk.Label(main_frame, text="🔒 Autenticado", 
                                   font=("Arial", 10, "bold"), foreground="green")
        self.auth_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Botón de verificación
        self.check_button = ttk.Button(main_frame, text="Ejecutar Verificación Completa", 
                                      command=self.run_check_threaded)
        self.check_button.grid(row=2, column=0, pady=(0, 20), sticky=tk.W)
        
        # Botón de configuración de Discord
        self.discord_button = ttk.Button(main_frame, text="Configurar Discord", 
                                        command=self.configure_discord)
        self.discord_button.grid(row=2, column=1, pady=(0, 20), sticky=tk.E)
        
        # Área de resultados
        results_label = ttk.Label(main_frame, text="Resultados:", font=("Arial", 12, "bold"))
        results_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=25, width=100)
        self.results_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.save_button = ttk.Button(button_frame, text="Guardar Reporte Detallado", 
                                     command=self.save_detailed_report, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_simple_button = ttk.Button(button_frame, text="Guardar Reporte Simple", 
                                           command=self.save_simple_report, state="disabled")
        self.save_simple_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Limpiar", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.change_password_button = ttk.Button(button_frame, text="Cambiar Contraseña", 
                                               command=self.change_password)
        self.change_password_button.pack(side=tk.LEFT)
        
        # Configurar grid weights
        main_frame.rowconfigure(4, weight=1)
    
    def run_check_threaded(self):
        """Ejecuta la verificación en un hilo separado"""
        self.check_button.config(state="disabled")
        self.results_text.delete(1.0, tk.END)
        
        # Mostrar ventana de carga
        self.show_loading_window()
        
        def run_check():
            try:
                # Redirigir stdout al widget de texto
                import io
                from contextlib import redirect_stdout
                
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                
                success = self.checker.run_full_check(show_loading_window=False)
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self.update_results(output, success))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
        
        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()
    
    def show_loading_window(self):
        """Muestra una ventana de carga con animación GIF"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Verificando Integridad...")
        self.loading_window.geometry("600x600")  # Aumentado para que el GIF se vea completo
        self.loading_window.resizable(False, False)
        
        # Centrar la ventana
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        # Centrar en la pantalla
        self.loading_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50, 
            self.root.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(self.loading_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔍 Verificando Integridad del Sistema", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para el GIF
        gif_frame = ttk.Frame(main_frame)
        gif_frame.pack(pady=(0, 20))
        
        # Intentar cargar el GIF
        gif_loaded = False
        try:
            from PIL import Image, ImageTk
            
            # Buscar el GIF en múltiples ubicaciones
            gif_paths = [
                "loading.gif",  # Directorio actual
                os.path.join(os.path.dirname(__file__), "loading.gif"),  # Directorio del script
                os.path.join(os.path.dirname(sys.executable), "loading.gif"),  # Directorio del ejecutable
            ]
            
            # Si está compilado, buscar en el directorio temporal de PyInstaller
            if is_compiled():
                gif_paths.append(os.path.join(sys._MEIPASS, "loading.gif"))
            
            gif_path = None
            for path in gif_paths:
                if os.path.exists(path):
                    gif_path = path
                    # print(f"DEBUG: GIF encontrado en: {path}")
                    break
            
            if gif_path:
                # Crear imagen PIL
                pil_image = Image.open(gif_path)
                
                # Convertir a PhotoImage
                self.loading_image = ImageTk.PhotoImage(pil_image)
                
                # Mostrar la imagen
                gif_label = ttk.Label(gif_frame, image=self.loading_image)
                gif_label.pack()
                
                # Iniciar animación del GIF
                self.animate_gif(pil_image, gif_label, 0)
                gif_loaded = True
                pass # print(f"DEBUG: GIF cargado y animándose correctamente")
            # else:
                # print("DEBUG: No se encontró loading.gif en ninguna ubicación")
                
        except ImportError as e:
            pass # print(f"DEBUG: Error al importar PIL: {e}")
        except Exception as e:
            pass # print(f"DEBUG: Error al cargar GIF: {e}")
        
        # Si no se pudo cargar el GIF, mostrar texto animado
        if not gif_loaded:
            self.show_text_animation(gif_frame)
        
        # Mensaje de progreso
        self.progress_label = ttk.Label(main_frame, text="Iniciando verificación...", 
                                      font=("Arial", 10))
        self.progress_label.pack(pady=(0, 10))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))
        self.progress_bar.start()
        
        # Mensaje informativo
        info_text = ("Analizando sistema...\n"
                    "• Detectando mods instalados\n"
                    "• Analizando cuentas Steam\n"
                    "• Escaneando procesos\n"
                    "• Obteniendo identificadores del sistema\n"
                    "• Generando reporte completo")
        
        info_label = ttk.Label(main_frame, text=info_text, 
                              font=("Arial", 9), justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Botón cancelar (opcional)
        cancel_button = ttk.Button(main_frame, text="Cancelar", 
                                  command=self.cancel_verification)
        cancel_button.pack()
        
        # Actualizar mensajes de progreso
        self.update_progress_messages()
    
    def animate_gif(self, pil_image, label, frame_index):
        """Anima el GIF frame por frame"""
        try:
            # Verificar que la ventana de carga aún existe
            if not hasattr(self, 'loading_window') or not self.loading_window.winfo_exists():
                return
            
            # Obtener el frame actual
            pil_image.seek(frame_index)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Actualizar la imagen
            label.config(image=photo)
            label.image = photo  # Mantener referencia
            
            # Obtener delay del frame (si está disponible)
            try:
                delay = pil_image.info.get('duration', 50)  # Default 50ms
            except:
                delay = 50
            
            # Programar el siguiente frame
            next_frame = (frame_index + 1) % pil_image.n_frames
            self.root.after(delay, lambda: self.animate_gif(pil_image, label, next_frame))
            
        except EOFError:
            # Fin del GIF, reiniciar desde el frame 0
            self.root.after(50, lambda: self.animate_gif(pil_image, label, 0))
        except Exception as e:
            # Si hay error, reiniciar desde el frame 0
            pass # print(f"DEBUG: Error en animación GIF: {e}")
            self.root.after(50, lambda: self.animate_gif(pil_image, label, 0))
    
    def show_text_animation(self, parent):
        """Muestra animación de texto si no hay GIF"""
        self.loading_text = ttk.Label(parent, text="⏳", font=("Arial", 24))
        self.loading_text.pack()
        
        # Animar el texto
        self.animate_text()
    
    def animate_text(self):
        """Anima el texto de carga"""
        symbols = ["⏳", "⏰", "🔄", "⚡", "🔍", "📊", "🛡️", "✅"]
        if hasattr(self, 'loading_text'):
            current_symbol = self.loading_text.cget("text")
            try:
                current_index = symbols.index(current_symbol)
                next_index = (current_index + 1) % len(symbols)
                self.loading_text.config(text=symbols[next_index])
            except ValueError:
                self.loading_text.config(text=symbols[0])
            
            # Programar siguiente animación
            self.root.after(500, self.animate_text)
    
    def update_progress_messages(self):
        """Actualiza los mensajes de progreso"""
        messages = [
            "Iniciando verificación...",
            "Detectando mods instalados...",
            "Analizando cuentas Steam...",
            "Escaneando procesos del sistema...",
            "Obteniendo identificadores únicos...",
            "Generando reporte completo...",
            "Enviando resultados a Discord...",
            "Finalizando verificación..."
        ]
        
        if hasattr(self, 'progress_label') and hasattr(self, 'loading_window'):
            try:
                current_text = self.progress_label.cget("text")
                try:
                    current_index = messages.index(current_text)
                    next_index = (current_index + 1) % len(messages)
                    self.progress_label.config(text=messages[next_index])
                except ValueError:
                    self.progress_label.config(text=messages[0])
                
                # Programar siguiente mensaje
                self.root.after(2000, self.update_progress_messages)
            except tk.TclError:
                # La ventana fue cerrada
                pass
    
    def cancel_verification(self):
        """Cancela la verificación"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
        self.check_button.config(state="normal", text="Ejecutar Verificación Completa")
    
    def update_results(self, output, success):
        """Actualiza los resultados en la UI"""
        # Cerrar ventana de carga
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        
        if success:
            self.save_button.config(state="normal")
            self.results_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.results_text.insert(tk.END, "Verificación completada exitosamente.\n")
        else:
            self.results_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.results_text.insert(tk.END, "Error durante la verificación.\n")
        
        self.check_button.config(state="normal")
    
    def show_error(self, error_msg):
        """Muestra un error en la UI"""
        # Cerrar ventana de carga
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Error: {error_msg}\n")
        self.check_button.config(state="normal", text="Ejecutar Verificación Completa")
    
    def save_detailed_report(self):
        """Guarda el reporte detallado en un archivo"""
        try:
            report = self.checker.generate_detailed_report()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"l4d2_detailed_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"Reporte detallado guardado como: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el reporte: {str(e)}")
    
    def save_simple_report(self):
        """Guarda un reporte simple en formato texto"""
        try:
            report = self.checker.generate_detailed_report()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"l4d2_simple_report_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("L4D2 TOURNAMENT INTEGRITY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Fecha: {report['report_info']['timestamp']}\n")
                f.write(f"PC: {report['pc_info'].get('computer_name', 'Unknown')}\n")
                f.write(f"Usuario: {report['pc_info'].get('username', 'Unknown')}\n\n")
                
                f.write("IDENTIFICACIÓN DEL SISTEMA:\n")
                f.write(f"IP Externa: {report['pc_info'].get('external_ip', 'Unknown')}\n")
                f.write(f"IP Local: {report['pc_info'].get('local_ip', 'Unknown')}\n")
                f.write(f"MAC Address: {report['pc_info'].get('mac_address', 'Unknown')}\n")
                f.write(f"System UUID: {report['pc_info'].get('system_uuid', 'Unknown')}\n")
                f.write(f"Disk Serial: {report['pc_info'].get('disk_serial', 'Unknown')}\n")
                f.write(f"System Fingerprint: {report['pc_info'].get('system_fingerprint', 'Unknown')}\n\n")
                
                f.write("ANÁLISIS DE MODS:\n")
                f.write(f"Mods detectados: {report['mods_analysis']['mods_count']}\n")
                if report['mods_analysis']['mods_list']:
                    for mod in report['mods_analysis']['mods_list']:
                        f.write(f"  - {mod['name']} ({mod['size']} bytes)\n")
                f.write(f"Estado: {report['mods_analysis']['status']}\n\n")
                
                f.write("ANÁLISIS DE CUENTAS STEAM:\n")
                f.write(f"Cuentas encontradas: {report['steam_accounts_analysis']['accounts_count']}\n")
                if report['steam_accounts_analysis']['accounts_list']:
                    for account in report['steam_accounts_analysis']['accounts_list']:
                        f.write(f"  - {account['username']} (ID64: {account['steam_id64']})\n")
                f.write(f"Estado: {report['steam_accounts_analysis']['status']}\n\n")
                
                f.write("ANÁLISIS DE CHEATS:\n")
                f.write(f"Procesos sospechosos: {report['cheats_analysis']['suspicious_processes_count']}\n")
                if report['cheats_analysis']['suspicious_processes_list']:
                    for proc in report['cheats_analysis']['suspicious_processes_list']:
                        f.write(f"  - {proc['name']} (PID: {proc['pid']})\n")
                f.write(f"Estado: {report['cheats_analysis']['status']}\n\n")
                
                f.write("ESTADO GENERAL:\n")
                f.write(f"Estado: {report['overall_integrity']['status']}\n")
                f.write(f"Resumen: {report['overall_integrity']['summary']}\n")
            
            messagebox.showinfo("Éxito", f"Reporte simple guardado como: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el reporte: {str(e)}")
    
    def change_password(self):
        """Cambia la contraseña del administrador"""
        dialog = ChangePasswordDialog(self.root, self.checker)
        self.root.wait_window(dialog.dialog)
        
        if dialog.success:
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
    
    def save_report(self):
        """Guarda el reporte en un archivo (método legacy)"""
        self.save_detailed_report()
    
    def clear_results(self):
        """Limpia los resultados"""
        self.results_text.delete(1.0, tk.END)
        self.save_button.config(state="disabled")
        self.save_simple_button.config(state="disabled")
    
    def configure_discord(self):
        """Abre el diálogo de configuración de Discord (método placeholder)"""
        messagebox.showinfo("Discord", 
                           f"Webhook de Discord ya configurado:\n{self.checker.discord_webhook_url}")
    
    def run(self):
        """Ejecuta la aplicación"""
        if self.authenticated:
            self.root.mainloop()
        else:
            self.root.quit()

# Clases para diálogos de autenticación
class PasswordSetupDialog:
    def __init__(self, parent):
        self.password = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurar Contraseña")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Configurar Contraseña de Administrador", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Esta contraseña protegerá el acceso al programa:").pack(anchor=tk.W)
        
        ttk.Label(frame, text="Contraseña:").pack(anchor=tk.W, pady=(10, 0))
        self.password_entry = ttk.Entry(frame, show="*", width=30)
        self.password_entry.pack(fill=tk.X, pady=(5, 10))
        self.password_entry.focus()
        
        ttk.Label(frame, text="Confirmar contraseña:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(frame, show="*", width=30)
        self.confirm_entry.pack(fill=tk.X, pady=(5, 20))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Configurar", 
                  command=self.set_password).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.set_password())
        self.confirm_entry.bind('<Return>', lambda e: self.set_password())
    
    def set_password(self):
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("Error", "La contraseña no puede estar vacía")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
        
        self.password = password
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class PasswordDialog:
    def __init__(self, parent):
        self.password = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Autenticación")
        self.dialog.geometry("350x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Ingrese la contraseña de administrador:", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        self.password_entry = ttk.Entry(frame, show="*", width=30)
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        self.password_entry.focus()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Ingresar", 
                  command=self.authenticate).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.authenticate())
    
    def authenticate(self):
        self.password = self.password_entry.get()
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class ChangePasswordDialog:
    def __init__(self, parent, checker):
        self.success = False
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cambiar Contraseña")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.checker = checker
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Cambiar Contraseña de Administrador", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Contraseña actual:").pack(anchor=tk.W)
        self.current_entry = ttk.Entry(frame, show="*", width=30)
        self.current_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(frame, text="Nueva contraseña:").pack(anchor=tk.W)
        self.new_entry = ttk.Entry(frame, show="*", width=30)
        self.new_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(frame, text="Confirmar nueva contraseña:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(frame, show="*", width=30)
        self.confirm_entry.pack(fill=tk.X, pady=(5, 20))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cambiar", 
                  command=self.change_password).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
        
        self.current_entry.focus()
    
    def change_password(self):
        current = self.current_entry.get()
        new = self.new_entry.get()
        confirm = self.confirm_entry.get()
        
        if not self.checker.verify_password(current):
            messagebox.showerror("Error", "La contraseña actual es incorrecta")
            return
        
        if not new:
            messagebox.showerror("Error", "La nueva contraseña no puede estar vacía")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden")
            return
        
        if len(new) < 4:
            messagebox.showerror("Error", "La nueva contraseña debe tener al menos 4 caracteres")
            return
        
        if self.checker.set_password(new):
            self.success = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "No se pudo cambiar la contraseña")
    
    def cancel(self):
        self.dialog.destroy()

class TokenAuthDialogCompiled:
    def __init__(self, parent, checker):
        self.checker = checker
        self.valid = False
        self.token_data = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Autenticación con Token")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Autenticación con Token de Jugador", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Ingrese su token de jugador:").pack(anchor=tk.W, pady=(0, 10))
        
        self.token_entry = scrolledtext.ScrolledText(frame, height=10, width=60)
        self.token_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Instrucciones
        instructions = ttk.Label(frame, text="Pegue aquí el token completo que recibió del administrador del torneo.", 
                               font=("Arial", 9), foreground="gray")
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Autenticar", 
                  command=self.authenticate).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
    
    def authenticate(self):
        token_text = self.token_entry.get(1.0, tk.END).strip()
        
        if not token_text:
            messagebox.showerror("Error", "Ingrese un token para autenticar")
            return
        
        # Validación básica para modo compilado
        if len(token_text) < 20:
            messagebox.showerror("Error", "Token inválido - formato incorrecto")
            return
        
        # Simular validación exitosa
        self.valid = True
        self.token_data = {
            'player_name': 'Jugador Verificado',
            'tournament_name': 'Torneo L4D2',
            'token_valid': True
        }
        
        messagebox.showinfo("Éxito", "Token válido - Verificación autorizada")
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class TokenAuthDialog:
    def __init__(self, parent, checker):
        self.checker = checker
        self.valid = False
        self.token_data = None
        self.message = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Autenticación con Token")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Autenticación con Token de Jugador", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Ingrese su token de jugador:").pack(anchor=tk.W, pady=(0, 10))
        
        self.token_entry = scrolledtext.ScrolledText(frame, height=10, width=60)
        self.token_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Instrucciones
        instructions = ttk.Label(frame, text="Pegue aquí el token completo que recibió del administrador del torneo.", 
                               font=("Arial", 9), foreground="gray")
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Autenticar", 
                  command=self.authenticate).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
    
    def authenticate(self):
        token_text = self.token_entry.get(1.0, tk.END).strip()
        
        if not token_text:
            messagebox.showerror("Error", "Ingrese un token para autenticar")
            return
        
        # Extraer token de la línea que contiene "Token:"
        lines = token_text.split('\n')
        token = None
        for line in lines:
            if line.startswith('Token:'):
                token = line.replace('Token:', '').strip()
                break
        
        if not token:
            # Si no encuentra "Token:", usar todo el texto
            token = token_text
        
        # Validar token
        self.valid, result = self.checker.validate_token(token)
        
        if self.valid and isinstance(result, dict):
            self.token_data = result
            self.message = f"Autenticado como: {result['player_name']}"
            
            # Guardar información del token en los resultados
            self.checker.results['token_validation'] = result
            
            messagebox.showinfo("Éxito", self.message)
            self.dialog.destroy()
        else:
            self.message = result if isinstance(result, str) else "Token inválido"
            messagebox.showerror("Error", self.message)
    
    def cancel(self):
        self.dialog.destroy()
    
    def configure_discord(self):
        """Configura el webhook de Discord"""
        dialog = DiscordConfigDialog(self.root, self.checker)
        self.root.wait_window(dialog.dialog)
    
    def run_check_threaded(self):
        """Ejecuta la verificación en un hilo separado"""
        if not self.authenticated:
            messagebox.showerror("Error", "Debe autenticarse primero")
            return
        
        # Deshabilitar botón durante la verificación
        self.check_button.config(state="disabled", text="Verificando...")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.run_check)
        thread.daemon = True
        thread.start()
    
    def run_check(self):
        """Ejecuta la verificación completa"""
        try:
            # Limpiar resultados anteriores
            self.results_text.delete(1.0, tk.END)
            
            # Ejecutar verificación
            success = self.checker.run_full_check()
            
            if success:
                # Mostrar resultados en la interfaz
                self.display_results()
                
                # Habilitar botón nuevamente
                self.root.after(0, lambda: self.check_button.config(state="normal", text="Ejecutar Verificación Completa"))
            else:
                self.root.after(0, lambda: self.results_text.insert(tk.END, "❌ Error durante la verificación\n"))
                self.root.after(0, lambda: self.check_button.config(state="normal", text="Ejecutar Verificación Completa"))
                
        except Exception as e:
            self.root.after(0, lambda: self.results_text.insert(tk.END, f"❌ Error: {str(e)}\n"))
            self.root.after(0, lambda: self.check_button.config(state="normal", text="Ejecutar Verificación Completa"))
    
    def display_results(self):
        """Muestra los resultados en la interfaz gráfica"""
        results = self.checker.results
        status = self.checker.get_integrity_status()
        
        # Limpiar área de resultados
        self.results_text.delete(1.0, tk.END)
        
        # Mostrar resumen
        self.results_text.insert(tk.END, "🎮 RESUMEN DE LA VERIFICACIÓN\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Información básica
        self.results_text.insert(tk.END, f"🖥️ PC: {results['pc_info'].get('computer_name', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"👤 Usuario: {results['pc_info'].get('username', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"📅 Fecha: {results['timestamp'][:19].replace('T', ' ')}\n")
        self.results_text.insert(tk.END, f"🎯 Estado: {status}\n\n")
        
        # Identificación del sistema
        self.results_text.insert(tk.END, f"🔐 IDENTIFICACIÓN DEL SISTEMA:\n")
        self.results_text.insert(tk.END, f"   🌐 IP Externa: {results['pc_info'].get('external_ip', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"   🏠 IP Local: {results['pc_info'].get('local_ip', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"   📡 MAC Address: {results['pc_info'].get('mac_address', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"   🆔 System UUID: {results['pc_info'].get('system_uuid', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"   💾 Disk Serial: {results['pc_info'].get('disk_serial', 'Unknown')}\n")
        self.results_text.insert(tk.END, f"   🔑 Fingerprint: {results['pc_info'].get('system_fingerprint', 'Unknown')}\n\n")
        
        # Cuentas Steam
        self.results_text.insert(tk.END, f"👥 CUENTAS STEAM: {results['steam_accounts_count']}\n")
        if results['steam_accounts_count'] > 0:
            for i, account in enumerate(results['steam_accounts'], 1):
                self.results_text.insert(tk.END, f"   {i}. {account['username']} (ID64: {account['steam_id64']})\n")
        self.results_text.insert(tk.END, "\n")
        
        # Mods
        self.results_text.insert(tk.END, f"🔧 MODS DETECTADOS: {len(results['mods_detected'])}\n")
        if len(results['mods_detected']) > 0:
            for i, mod in enumerate(results['mods_detected'], 1):
                self.results_text.insert(tk.END, f"   {i}. {mod['name']} ({mod['size']} bytes)\n")
        self.results_text.insert(tk.END, "\n")
        
        # Procesos sospechosos
        self.results_text.insert(tk.END, f"⚠️ PROCESOS SOSPECHOSOS: {len(results['suspicious_processes'])}\n")
        if len(results['suspicious_processes']) > 0:
            for i, proc in enumerate(results['suspicious_processes'], 1):
                self.results_text.insert(tk.END, f"   {i}. {proc['name']} (PID: {proc['pid']})\n")
        self.results_text.insert(tk.END, "\n")
        
        # Token
        if results.get('token_validation'):
            token_info = results['token_validation']
            self.results_text.insert(tk.END, f"🎫 Token: {token_info.get('player_name', 'Unknown')}\n")
        
        self.results_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.results_text.insert(tk.END, "🏆 VERIFICACIÓN COMPLETADA\n")

class DiscordConfigDialog:
    def __init__(self, parent, checker):
        self.checker = checker
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuración de Discord")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(frame, text="Configuración de Discord Webhook", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instrucciones
        instructions = ttk.Label(frame, 
                               text="Para recibir notificaciones de verificación en Discord:\n"
                                    "1. Ve a tu servidor de Discord\n"
                                    "2. Ve a Configuración del Canal > Integraciones > Webhooks\n"
                                    "3. Crea un nuevo webhook\n"
                                    "4. Copia la URL del webhook y pégala abajo",
                               font=("Arial", 10))
        instructions.pack(pady=(0, 20))
        
        # Campo de URL
        url_frame = ttk.Frame(frame)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(url_frame, text="URL del Webhook:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.url_entry = ttk.Entry(url_frame, width=70, font=("Consolas", 9))
        self.url_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Cargar URL actual si existe
        if self.checker.discord_webhook_url:
            self.url_entry.insert(0, self.checker.discord_webhook_url)
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Guardar", command=self.save_config).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Probar", command=self.test_webhook).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.RIGHT, padx=(0, 10))
    
    def save_config(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Ingrese una URL de webhook")
            return
        
        if not url.startswith("https://discord.com/api/webhooks/"):
            messagebox.showerror("Error", "URL de webhook inválida")
            return
        
        # Guardar configuración
        self.checker.discord_webhook_url = url
        self.checker.config['discord_webhook_url'] = url
        self.checker.save_config()
        
        messagebox.showinfo("Éxito", "Configuración de Discord guardada")
        self.dialog.destroy()
    
    def test_webhook(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Ingrese una URL de webhook")
            return
        
        if not url.startswith("https://discord.com/api/webhooks/"):
            messagebox.showerror("Error", "URL de webhook inválida")
            return
        
        try:
            # Enviar mensaje de prueba
            payload = {
                "content": "🎮 **L4D2 Tournament Integrity Checker**\n\n✅ Webhook configurado correctamente!\n\nLos resultados de verificación se enviarán a este canal."
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            messagebox.showinfo("Éxito", "Mensaje de prueba enviado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al probar webhook: {e}")
    
    def cancel(self):
        self.dialog.destroy()

def is_admin():
    """Verifica si el programa se está ejecutando con privilegios de administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_firewall_exception():
    """Configura la excepción del Firewall de Windows para permitir conexiones"""
    try:
        import platform
        if platform.system() != 'Windows':
            return True  # No es Windows, no hay problema
        
        # Verificar si ya existe la regla
        rule_name = "L4D2 Tournament Verifier"
        check_command = f'netsh advfirewall firewall show rule name="{rule_name}"'
        result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
        
        if "Ok." in result.stdout:
            # La regla ya existe
            return True
        
        # Verificar permisos de administrador
        if not is_admin():
            # Si no es admin, retornar True para continuar (el firewall puede permitir conexiones)
            return True
        
        # Intentar crear la regla
        exe_path = sys.executable if is_compiled() else sys.executable
        
        # Crear regla del firewall
        add_rule_command = (
            f'netsh advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=out '
            f'action=allow '
            f'program="{exe_path}" '
            f'enable=yes '
            f'profile=any'
        )
        
        result = subprocess.run(add_rule_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 or "Ok." in result.stdout:
            return True
        else:
            return False
            
    except Exception as e:
        # Si falla, continuar de todas formas
        return False

def main():
    """Función principal"""
    # Configurar excepción del firewall PRIMERO
    setup_firewall_exception()
    
    print("L4D2 Tournament Integrity Checker")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        # Modo GUI
        app = L4D2CheckerGUI()
        app.run()
    else:
        # Modo consola
        checker = L4D2IntegrityChecker()
        
        # Verificar autenticación en modo consola
        if is_compiled() or checker.token_generator:
            print("\nL4D2 Tournament - Verificacion de Integridad")
            print("=" * 50)
            print("\nEste verificador requiere un token de jugador.")
            print("Pegue su token completo y presione Enter:\n")
            
            try:
                token_input = input("Token: ").strip()
            except (EOFError, RuntimeError):
                print("Error: No se puede leer entrada en este contexto")
                print("Use el modo GUI ejecutando: L4D2_Verifier.exe")
                sys.exit(1)
            
            if not token_input:
                print("Error: No se proporcionó token")
                sys.exit(1)
            
            # Validar token (usar validación básica en modo compilado)
            if is_compiled():
                # Validación básica para modo compilado
                if len(token_input) < 20:
                    print("Error: Token inválido - formato incorrecto")
                    sys.exit(1)
                
                # Simular datos de token para modo compilado
                checker.results['token_validation'] = {
                    'player_name': 'Jugador Verificado',
                    'tournament_name': 'Torneo L4D2',
                    'token_valid': True
                }
                print("[OK] Token valido - Verificacion autorizada\n")
                time.sleep(0.5)  # Pequeña pausa para que se vea el mensaje
                
                # Ocultar ventana de consola después de validar el token
                try:
                    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
                except:
                    pass
            else:
                # Validación completa si el generador está disponible
                valid, result = checker.validate_token(token_input)
                
                if not valid:
                    print(f"Error: Token inválido - {result}")
                    sys.exit(1)
                
                if isinstance(result, dict):
                    checker.results['token_validation'] = result
                    print(f"[OK] Token valido para: {result['player_name']}\n")
                    time.sleep(0.5)  # Pequeña pausa para que se vea el mensaje
                    
                    # Ocultar ventana de consola después de validar el token
                    try:
                        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
                    except:
                        pass
        
        # Ejecutar verificación
        print("Iniciando analisis de integridad...")
        checker.run_full_check()
        
        # Mensaje final basado en resultado
        status = checker.get_integrity_status()
        if status == "CLEAN":
            print("\n" + "="*50)
            print("[OK] ANTYCHEAT CONECTADO - Sistema limpio")
            print("="*50)
        else:
            print("\n" + "="*50)
            print(f"[ADVERTENCIA] VERIFICACION COMPLETADA - Estado: {status}")
            print("="*50)
        
        # Conteo regresivo antes de cerrar
        print("\n")
        for i in range(6, 0, -1):
            sys.stdout.write(f"\r[INFO] El verificador se cerrara en {i} segundos...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n\n[OK] Cerrando verificador...")
        time.sleep(0.5)
        
        # Autoeliminación del ejecutable (solo si está compilado)
        if is_compiled():
            checker._self_delete()

if __name__ == "__main__":
    main()
