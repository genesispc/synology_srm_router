"""Synology SRM Sensors.
Example:
  - platform: synology_srm
    #Required
    name: Router1
    host: 192.168.0.1
    password: !secret synology_srm_password

    #Optional
    port: 8001
    username: admin
    ssl: true
    verify_ssl: false
"""