FROM php:7.0-apache

ADD ./php.ini /usr/local/etc/php/

RUN a2enmod speling && \
        a2enmod rewrite && \
        a2enmod proxy && \
        a2enmod ssl

RUN apt-get update && apt-get install -y \
  python3 libapache2-mod-wsgi-py3

RUN mkdir -p /var/www/budgetprops-dev/logs/

RUN apt-get update && apt-get install -y \
  libapache2-mod-auth-cas

RUN mkdir -p /var/cache/mod_auth_cas/

COPY apache/ /etc/apache2/conf-enabled/

RUN apt-get update && apt-get install -y \
  libpq-dev && \
  docker-php-ext-install pgsql

RUN mkdir -p /usr/share/pear/Twig

COPY ./Twig /usr/share/pear/Twig/

RUN mkdir -p /var/www/budgetprops-dev/htdocs/views/
RUN mkdir -p /var/www/budgetprops-dev/logs/

COPY ./htdocs /var/www/budgetprops-dev/htdocs/

RUN chmod -R 777 /var/www/budgetprops-dev/htdocs/views
RUN chmod -R 777 /var/cache/mod_auth_cas
