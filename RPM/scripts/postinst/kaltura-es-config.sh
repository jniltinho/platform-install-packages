#!/bin/sh -e

KALTURA_FUNCTIONS_RC=`dirname $0`/kaltura-functions.rc
if [ ! -r "$KALTURA_FUNCTIONS_RC" ];then
        OUT="${BRIGHT_RED}ERROR:could not find $KALTURA_FUNCTIONS_RC so, exiting..${NORMAL}"
        echo -en $OUT
        exit 3
fi
. $KALTURA_FUNCTIONS_RC
if ! rpm -q kaltura-elasticsearch;then
        echo -e "${BRIGHT_RED}Exiting as kaltura-elasticsearch is not installed.
This MAY be because the installation of it was skipped do to SELinux being in 'Enforcing' mode.
Please review: https://github.com/kaltura/platform-install-packages/blob/master/doc/install-kaltura-redhat-based.md#disable-selinux---required-currently-kaltura-cant-run-properly-with-selinux
And re-run:
# yum install kaltura-elasticsearch

${NORMAL}"
        exit 2 
fi
TIME_STAMP=`date +%Y_%m`
ES_HOST=127.0.0.1
ES_PORT=9200
set +e
# Elasticsearch 7 (EL9) bundles its own JDK and uses the elasticsearch-7 mappings shipped with the server
ES_MAJOR=`rpm -q elasticsearch --queryformat %{version} 2>/dev/null | cut -d. -f1`
if [ "$ES_MAJOR" -ge 7 ] 2>/dev/null;then
	MAPPING_DIR=$APP_DIR/configurations/elastic/mapping/elasticsearch-7
	BEACON_MAPPING_DIR=$APP_DIR/plugins/beacon/config/mapping/elasticsearch-7
	ES_REPLICAS=0
else
	ES_MAJOR=6
	MAPPING_DIR=$APP_DIR/configurations/elastic/mapping
	BEACON_MAPPING_DIR=$APP_DIR/plugins/beacon/config/mapping
	ES_REPLICAS=1
yum install -y java-1.8.0-openjdk-headless
JDK_18_VERSION=`rpm -q java-1.8.0-openjdk-headless --queryformat %{version}-%{release}.%{arch}`
alternatives --install /usr/bin/java java /usr/lib/jvm/java-1.8.0-openjdk-$JDK_18_VERSION/jre/bin/java 1
update-alternatives --set java /usr/lib/jvm/java-1.8.0-openjdk-$JDK_18_VERSION/jre/bin/java 
if ! rpm -q "elasticsearch-oss" >/dev/null 2>&1 && ! rpm -q "elasticsearch" >/dev/null 2>&1 ;then
        yum localinstall -y https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-oss-6.5.4.rpm 
fi
fi

if [ -x /sbin/chkconfig -a -r /etc/init.d/elasticsearch ];then
    /sbin/chkconfig --add elasticsearch
else
    /usr/bin/systemctl enable elasticsearch.service >/dev/null 2>&1 ||:
fi

set -e
# should no longer be needed
#sed -i 's@^\(\s*"type" : \)"boolean"\s*@\1"keyword"@g' $APP_DIR/configurations/elastic/mapping/*.json
mv /etc/elasticsearch/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml.orig
sed -e "s#@BASE_DIR@#$BASE_DIR#g" -e "s#@LOG_DIR@#$LOG_DIR#g" -e "s#@HOSTNAME@#`hostname`#g" $APP_DIR/configurations/elastic/elasticsearch.template.yml > /etc/elasticsearch/elasticsearch.yml

if [ "$ES_MAJOR" -ge 7 ];then
	# single node All-In-One with a fixed 1 GB heap (tune in /etc/elasticsearch/jvm.options.d/kaltura.options)
	sed -i '/^node\.\(master\|data\):/d' /etc/elasticsearch/elasticsearch.yml
	echo "discovery.type: single-node" >> /etc/elasticsearch/elasticsearch.yml
	[ -f /etc/elasticsearch/jvm.options.d/kaltura.options ] || printf -- '-Xms1g\n-Xmx1g\n' > /etc/elasticsearch/jvm.options.d/kaltura.options
else
echo "ES_JAVA_OPTS=\"-Djna.tmpdir=$BASE_DIR/var/lib/elasticsearch/tmp -Djava.io.tmpdir=$BASE_DIR/var/lib/elasticsearch/tmp\"" >> /etc/sysconfig/elasticsearch
echo JAVA_HOME="/usr/lib/jvm/java-1.8.0-openjdk-$JDK_18_VERSION" >> /etc/sysconfig/elasticsearch 
fi

chown -R elasticsearch $LOG_DIR/elasticsearch $BASE_DIR/var/lib/elasticsearch
if [ ! -d /usr/share/elasticsearch/plugins/analysis-icu ];then
        /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch analysis-icu
fi
service elasticsearch restart
mkdir -p $APP_DIR/configurations/elastic/populate
chown kaltura $APP_DIR/configurations/elastic/populate
set +e
ATTEMPT=0
while ! curl -f "http://127.0.0.1:9200/" >> /dev/null 2>&1;do
        sleep 5
        if [ $ATTEMPT -eq 22 ];then 
                echo "We've waited a minute and the ES daemon is still unreachable, we're giving up:("
                exit;
        fi 
        ATTEMPT=`expr $ATTEMPT + 1`
done
set -e
if ! curl -f -I -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_entry";then
        set -e
        curl -f -XPUT -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_entry" -d @$MAPPING_DIR/entry_mapping.json
fi
set +e
if ! curl -f -I -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_category";then
        set -e
        curl -f -XPUT -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_category" -d @$MAPPING_DIR/category_mapping.json
fi
set +e
if ! curl -f -I -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_kuser";then
        #set -e 
        curl -f -XPUT -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_kuser" -d @$MAPPING_DIR/kuser_mapping.json
fi
set +e
if ! curl -f -I -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_search_history";then
        set -e
        curl -f -XPUT -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/kaltura_search_history" -d @$MAPPING_DIR/search_history_mapping.json
fi
set +e
if ! curl -f -I -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/_aliases?pretty";then
        set -e
        curl -f -XPOST -H "Content-Type: application/json" "http://$ES_HOST:$ES_PORT/_aliases?pretty" -d '{"actions": [{"add":{"index":"kaltura_search_history","alias": "search_history_index"}},{"add":{"index":"kaltura_search_history","alias": "search_history_search"}}]}'
fi
set +e
if ! curl -f -I http://$ES_HOST:$ES_PORT/beacon_entry_index_$TIME_STAMP;then
        set -e
        curl -f -XPUT http://$ES_HOST:$ES_PORT/beacon_entry_index_$TIME_STAMP --data-binary @$BEACON_MAPPING_DIR/beacon_entry_index.json -H 'Content-Type: application/json'
fi
set +e
if ! curl -f -I http://$ES_HOST:$ES_PORT/beacon_entry_server_node_index_$TIME_STAMP;then
        set -e
        curl -f -XPUT http://$ES_HOST:$ES_PORT/beacon_entry_server_node_index_$TIME_STAMP --data-binary @$BEACON_MAPPING_DIR/beacon_entry_server_node_index.json -H 'Content-Type: application/json'
fi
set +e
if ! curl -f -I http://$ES_HOST:$ES_PORT/beacon_scheduled_resource_index_$TIME_STAMP;then
        set -e
        curl -f -XPUT http://$ES_HOST:$ES_PORT/beacon_scheduled_resource_index_$TIME_STAMP --data-binary @$BEACON_MAPPING_DIR/beacon_scheduled_resource_index.json -H 'Content-Type: application/json'
fi
set +e
if ! curl -f -I http://$ES_HOST:$ES_PORT/beacon_server_node_index_$TIME_STAMP ;then
        set -e
        curl -f -XPUT http://$ES_HOST:$ES_PORT/beacon_server_node_index_$TIME_STAMP --data-binary @$BEACON_MAPPING_DIR/beacon_server_node_index.json -H 'Content-Type: application/json'
fi


set +e
for ITEM in beacon_entry_index_$TIME_STAMP beacon_entry_server_node_index_$TIME_STAMP beacon_scheduled_resource_index_$TIME_STAMP beacon_server_node_index_$TIME_STAMP kaltura_entry kaltura_kuser kaltura_category;do 
        curl -f -XPUT http://$ES_HOST:$ES_PORT/$ITEM/_settings -H 'Content-Type: application/json' -d"{\"index\" : {\"number_of_replicas\" : \"$ES_REPLICAS\"}}";
done
sed -i "s#@MONTH_DAY@#$TIME_STAMP#g" /etc/elasticsearch/aliases/aliases.json
curl -f -XPOST "http://$ES_HOST:$ES_PORT/_aliases?pretty" -H 'Content-Type: application/json' -d @/etc/elasticsearch/aliases/aliases.json

set -e

echo "elasticCluster = kaltura
elasticServer = $ES_HOST 
elasticPort = $ES_PORT
" >$APP_DIR/configurations/elastic/populate/`hostname`.ini
sed -i -e "s#@ELASTIC_PORT@#$ES_PORT#g" -e "s#@ELASTIC_HOST@#$ES_HOST#g" -e "s#@BEACONS_ELASTIC_HOST@#$ES_HOST#g" -e "s#@BEACONS_ELASTIC_PORT@#$ES_PORT#g" -e "s#@CURL_TIMEOUT_IN_SEC@#10#g" $APP_DIR/configurations/elastic.ini
# ES 7 returns hits.total as an object; Kaltura defaults to the ES 5 client behavior
if [ "$ES_MAJOR" -ge 7 ];then
	echo "elasticVersion = 7" >> $APP_DIR/configurations/elastic/populate/`hostname`.ini
	grep -q '^elasticVersion' $APP_DIR/configurations/elastic.ini || sed -i '0,/^elasticPort = .*/s//&\nelasticVersion = 7/' $APP_DIR/configurations/elastic.ini
fi
find $APP_DIR/cache/ -type f -exec rm {} \;
find $APP_DIR/cache/ -type d -exec chmod 775 {} \;  
find $APP_DIR/cache/ -type f -exec chmod 664 {} \;  
chown -R kaltura.apache $BASE_DIR/app/cache/

service httpd restart
service memcached restart
set +e
/etc/init.d/kaltura-elastic-populate stop || true
/etc/init.d/kaltura-elastic-populate start || true

