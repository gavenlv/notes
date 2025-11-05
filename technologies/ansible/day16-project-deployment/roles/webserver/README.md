# Webserver Role

This role configures the web server for the application.

## Features

- Installs and configures web server software (Nginx/Apache)
- Sets up virtual hosts
- Configures SSL certificates
- Manages web server services

## Variables

### Defaults
- `webserver_package`: The package name for the web server (default: nginx)
- `webserver_service`: The service name for the web server (default: nginx)
- `webserver_port`: The port the web server listens on (default: 80)
- `webserver_ssl_port`: The SSL port the web server listens on (default: 443)

### OS-Specific Variables
- `webserver_user`: The user the web server runs as
- `webserver_group`: The group the web server runs as
- `webserver_config_path`: The path to the web server configuration
- `webserver_sites_path`: The path to the web server sites configuration

## Tasks

- Install web server package
- Configure web server
- Set up virtual hosts
- Configure SSL (if enabled)
- Start and enable web server service

## Templates

- `nginx.conf.j2`: Main Nginx configuration
- `site.conf.j2`: Virtual host configuration
- `ssl.conf.j2`: SSL configuration