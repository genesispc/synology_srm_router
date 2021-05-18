# synology_srm_router
Synology Router Details for Home Assistant

This is code obtained from here: 
https://github.com/i00/Chatter/issues/1

Right Side
First of all extract synology_srm_router.zip to your config\custom_components folder (make sure you use this version ... I have updated it to work with the latest version of HA)
setup the sensors below in your config like follows for router info:
binary_sensor:
  - platform: ping
    host: 8.8.8.8
    name: Online
    count: 1
    scan_interval: 300
sensor:
  - platform: synology_srm_router
    host: SynologyRouter.local
    password: !secret SynologyRouter
    monitored_conditions:
      - core.list_ddns_extip
      - core.get_system_utilization
      - core.list_ddns_record
  - platform: scrape
    resource: https://www.whoismyisp.org
    select: ".isp"
    name: 'Internet Provider'
    scan_interval: 60 #1 mins
  - platform: template
    sensors:
      wan_download:
        value_template: "{% set i = namespace() %}{% set i.i = 0 %}{% for item in states.sensor.synology_srm.attributes.core_get_system_utilization.network if item.device|regex_match('^(usbnet|ppp)', ignorecase=true) %}{% set i.i = i.i + item.rx %}{% endfor %}{{ ((i.i / 1024 / 1024) * 8)|round(2) }}"
        friendly_name: Download
        unit_of_measurement: Mbit/s
        icon_template: 'mdi:download'
      wan_upload:
        value_template: "{% set i = namespace() %}{% set i.i = 0 %}{% for item in states.sensor.synology_srm.attributes.core_get_system_utilization.network if item.device|regex_match('^(usbnet|ppp)', ignorecase=true) %}{% set i.i = i.i + item.tx %}{% endfor %}{{ ((i.i / 1024 / 1024) * 8)|round(2) }}"
        friendly_name: Upload
        unit_of_measurement: Mbit/s
        icon_template: 'mdi:upload'
Extract resources.zip to your config\www folder (be aware this contains different resources to the left side; some components are the same; so you can either replace or skip the conflicts)
In HA go to "Configuration > Lovelace Dashboards >Resources"
Add in the following resources as javascript modules (skip any that you may have added in left side in italic):
/local/resources/card-mod.js?v=13
/local/resources/html-template-card.js?v=1.0.2
/local/resources/mini-graph-card-bundle.js?v=0.9.3
/local/resources/multiple-entity-row.js?v=3.1.1
/local/resources/template-entity-row.js?v=1.1.0
/local/resources/vertical-stack-in-card.js?v=0.1.3
Add a manual Lovelace card with the following content:
cards:
  - entities:
      - entity: binary_sensor.online
        icon: 'mdi:web'
        name: Status
        type: 'custom:multiple-entity-row'
      - entity: sensor.internet_provider
        icon: 'mdi:web'
        name: Provider
      - entity: sensor.pi_hole_ads_percentage_blocked_today
        name: Adverts Blocked (Last 24 Hours)
      - icon: 'mdi:server-network'
        name: Devices
        state: >
          {% set force_upadte = states.input_number.min_timer.state %} {% set i
          = namespace() %} {% set i.i = 0 %}{% for item in states.device_tracker
          if item.attributes.scanner == 'SynologySrmDeviceScanner' and
          item.state == 'home' %}{% set i.i = i.i + 1 %}{% endfor %}{{ i.i }}
        tap_action:
          action: navigate
          navigation_path: /lovelace/network
        type: 'custom:template-entity-row'
      - label: Routing Load
        type: section
      - icon: 'mdi:memory'
        name: CPU
        state: >
          {% set cpu =

          states.sensor.synology_srm.attributes.core_get_system_utilization.cpu
          -%}

          {{ cpu.other_load + cpu.system_load + cpu.user_load }} %
        type: 'custom:template-entity-row'
      - name: null
        secondary: Last 15 min average
        state: >
          {% set cpu =
          states.sensor.synology_srm.attributes.core_get_system_utilization.cpu
          -%}

          {% set cores = 2 -%}

          {{ (cpu['15min_load']/cores)|int }} %
        type: 'custom:template-entity-row'
      - icon: 'mdi:chip'
        name: Memory
        state: >
          {% set memory =
          states.sensor.synology_srm.attributes.core_get_system_utilization.memory
          -%} {{ memory.real_usage }} % ({{ (memory.memory_size / 1024 *
          memory.real_usage /100)|int }} / {{ (memory.memory_size / 1024)|int }}
          MB)
        type: 'custom:template-entity-row'
      - label: External Access
        type: section
    show_header_toggle: false
    style: |
      .card-content {
        padding-bottom: 0 !important;
      }
    title: Internet and Network
    type: entities
  - card:
      content: >-
        <table width=100%>

        {% set ddns_extip =
        states.sensor.synology_srm.attributes.core_list_ddns_extip -%}

        {% for item in ddns_extip -%}
          <tr><td valign=top>IP ({{ item.type }}):</td><td>{{ item.ip }}</td></tr>
          <tr><td valign=top>IPv6 ({{ item.type }}):</td><td>{{ item.ipv6 }}</td></tr>
        {% endfor -%}

        {% set ddns_extip =
        states.sensor.synology_srm.attributes.core_list_ddns_record -%}

        {% for item in ddns_extip.records %}
          {% set Preamble = "<b style='color: darkred;'>" if item.status != 'service_ddns_normal' else '' %}
          {% set Postamble = '<br>State: ' + item.status + '</b>' if item.status != 'service_ddns_normal' else '' %}
          <tr><td valign=top>{{ item.provider }}:</td><td>{{ Preamble }}{{ item.hostname }}{{ Postamble }}</td></tr>
        {% endfor -%}

        </table>
      ignore_line_breaks: true
      type: 'custom:html-template-card'
    style: |
      ha-card {
        padding-top: 0 !important;
        padding-left: 16px !important;
        padding-bottom: 0 !important;
      }
    type: 'custom:mod-card'
  - entities:
      - label: Traffic and Benchmarks (last 24 hours)
        type: section
    show_header_toggle: false
    style: |
      .card-content {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
      }
    type: entities
  - cards:
      - aggregate_func: ave
        entities:
          - entity: sensor.wan_download
            index: 0
            name: Traffic
          - color: '#0000FF44'
            entity: sensor.speedtest_download
            index: 1
            name: Speed Test
        font_size: 75
        group_by: hour
        height: 200
        hours_to_show: 24
        line_color: '#0000FF'
        lower_bound: 0
        name: Download
        show:
          icon: false
          labels: true
          points: hover
        style: |
          ha-card {
            padding-top: 0 !important;
            padding-right: 2px !important;
          }
          .header,
          .graph__legend {
            padding-bottom: 0 !important;
          }
          .info {
            display: none !important;
          }
          .label--max,
          .label--min {
            box-shadow: unset !important;
          }
        type: 'custom:mini-graph-card'
      - aggregate_func: ave
        entities:
          - entity: sensor.wan_upload
            index: 0
            name: Traffic
          - color: '#e74c3c44'
            entity: sensor.speedtest_upload
            index: 1
            name: Speed Test
        font_size: 75
        group_by: hour
        height: 200
        hours_to_show: 24
        line_color: '#e74c3c'
        lower_bound: 0
        name: Upload
        show:
          icon: false
          labels: true
          points: hover
        style: |
          ha-card {
            padding-top: 0 !important;
            padding-left: 1px !important;
            padding-right: 1px !important;
          }
          .header,
          .graph__legend {
            padding-bottom: 0 !important;
          }
          .info {
            display: none !important;
          }
          .label--max,
          .label--min {
            box-shadow: unset !important;
          }
        type: 'custom:mini-graph-card'
      - aggregate_func: ave
        entities:
          - entity: sensor.speedtest_ping
            index: 0
            name: Ping
          - color: '#0000FF44'
            entity: sensor.wan_download
            index: 1
            name: Download
            show_fill: false
            show_legend: false
            y_axis: secondary
          - color: '#e74c3c44'
            entity: sensor.wan_upload
            index: 2
            name: Upload
            show_fill: false
            show_legend: false
            y_axis: secondary
          - entity: sensor.speedtest_download
            index: 3
            show_fill: false
            show_legend: false
            show_line: false
            show_points: false
            y_axis: secondary
          - entity: sensor.speedtest_upload
            index: 4
            show_fill: false
            show_legend: false
            show_line: false
            show_points: false
            y_axis: secondary
        font_size: 75
        group_by: hour
        height: 200
        hours_to_show: 24
        line_color: var(--accent-color)
        lower_bound_secondary: 0
        show:
          icon_adaptive_color: false
          labels: true
          labels_secondary: false
          points: hover
        style: |
          ha-card {
            padding-top: 0 !important;
            padding-left: 1px !important;
            padding-right: 1px !important;
          }
          .header,
          .graph__legend {
            padding-bottom: 0 !important;
          }
          .info {
            display: none !important;
          }
          .label--max,
          .label--min {
            box-shadow: unset !important;
          }
        type: 'custom:mini-graph-card'
    type: horizontal-stack
type: 'custom:vertical-stack-in-card'
