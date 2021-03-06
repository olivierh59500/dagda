import json
import os
import sys
import requests
from cli.dagda_cli_parser import DagdaCLIParser
from api.dagda_server import DagdaServer


# -- Get Dagda server base url
def get_dagda_base_url():
    # -- Load env variables
    try:
        dagda_host = os.environ['DAGDA_HOST']
    except KeyError:
        print('dagda.py: error: DAGDA_HOST environment variable is not set.', file=sys.stderr)
        exit(1)

    try:
        dagda_port = os.environ['DAGDA_PORT']
    except KeyError:
        print('dagda.py: error: DAGDA_PORT environment variable is not set.', file=sys.stderr)
        exit(1)

    # -- Return Dagda server base url
    return 'http://' + dagda_host + ':' + dagda_port + '/v1'


# -- Main function
def main(parsed_args):
    # -- Init
    cmd = parsed_args.get_command()
    parsed_args = parsed_args.get_extra_args()

    # Executes start sub-command
    if cmd == 'start':
        ds = DagdaServer(dagda_server_host=parsed_args.get_server_host(),
                         dagda_server_port=parsed_args.get_server_port(),
                         mongodb_host=parsed_args.get_mongodb_host(),
                         mongodb_port=parsed_args.get_mongodb_port())
        ds.run()

    else:
        dagda_base_url = get_dagda_base_url()
        # -- Executes vuln sub-command
        if cmd == 'vuln':
            if parsed_args.is_initialization_required():
                # Init db
                r = requests.post(dagda_base_url + '/vuln/init')
            elif parsed_args.is_init_status_requested():
                # Retrieves the init status
                r = requests.get(dagda_base_url + '/vuln/init-status')
            else:
                if parsed_args.get_cve():
                    # Gets products by CVE
                    r = requests.get(dagda_base_url + '/vuln/cve/' + parsed_args.get_cve())
                elif parsed_args.get_bid():
                    # Gets products by BID
                    r = requests.get(dagda_base_url + '/vuln/bid/' + str(parsed_args.get_bid()))
                elif parsed_args.get_exploit_db_id():
                    # Gets products by Exploit DB Id
                    r = requests.get(dagda_base_url + '/vuln/exploit/' + str(parsed_args.get_exploit_db_id()))
                else:
                    # Gets CVEs, BIDs and Exploit_DB Ids by product and version
                    if not parsed_args.get_product_version():
                        r = requests.get(dagda_base_url + '/vuln/products/' + parsed_args.get_product())
                    else:
                        r = requests.get(dagda_base_url + '/vuln/products/' + parsed_args.get_product() + '/' +
                                         parsed_args.get_product_version())

        # Executes check sub-command
        elif cmd == 'check':
            if parsed_args.get_docker_image_name():
                r = requests.post(dagda_base_url + '/check/images/' + parsed_args.get_docker_image_name())
            else:
                r = requests.post(dagda_base_url + '/check/containers/' + parsed_args.get_container_id())

        # Executes history sub-command
        elif cmd == 'history':
            # Gets the history
            query_params = ''
            if parsed_args.get_report_id() is not None:
                query_params = '?id=' + parsed_args.get_report_id()
            r = requests.get(dagda_base_url + '/history/' + parsed_args.get_docker_image_name() + query_params)

        # Executes monitor sub-command
        elif cmd == 'monitor':
            if parsed_args.is_start():
                r = requests.post(dagda_base_url + '/monitor/containers/' + parsed_args.get_container_id() + '/start')
            elif parsed_args.is_stop():
                r = requests.post(dagda_base_url + '/monitor/containers/' + parsed_args.get_container_id() + '/stop')

        # -- Print cmd output
        if r is not None:
            print(json.dumps(json.loads(r.content.decode('utf-8')), sort_keys=True, indent=4))


if __name__ == "__main__":
    main(DagdaCLIParser())
