<IfModule mod_ssl.c>
<VirtualHost telepresence.compete.com:443>
	ServerAdmin telepresence@compete.com

	DocumentRoot /var/www/telepresence.compete.com

        WSGIScriptAlias / /var/www/telepresence.compete.com/telepresence/wsgi.py

        WSGIDaemonProcess telepresence.compete.com python-path=/var/www/telepresence.compete.com:/var/www/telepresence.compete.com/venv/lib/python2.7/site-packages
        WSGIProcessGroup telepresence.compete.com

	<Directory /var/www/telepresence.compete.com>
          <Files wsgi.py>
            Order deny,allow
            Allow from all
          </Files>
	</Directory>

        Alias /static/ /var/www/telepresence.compete.com/static/

        <Directory /var/www/telepresence.compete.com/static>
          Order deny,allow
          Allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error-telepresence.compete.com.log

	LogLevel info

	CustomLog ${APACHE_LOG_DIR}/ssl_access-telepresence.compete.com.log combined

	SSLEngine on

	SSLCertificateFile    /etc/ssl/certs/ssl-cert-snakeoil.pem
	SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

	#   Notice: Most problems of broken clients are also related to the HTTP
	#   keep-alive facility, so you usually additionally want to disable
	#   keep-alive for those clients, too. Use variable "nokeepalive" for this.
	#   Similarly, one has to force some clients to use HTTP/1.0 to workaround
	#   their broken HTTP/1.1 implementation. Use variables "downgrade-1.0" and
	#   "force-response-1.0" for this.
	BrowserMatch "MSIE [2-6]" \
		nokeepalive ssl-unclean-shutdown \
		downgrade-1.0 force-response-1.0
	# MSIE 7 and newer should be able to use keepalive
	BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown

</VirtualHost>
</IfModule>
