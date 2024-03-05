def del_org_header(authorization, orgid=None):
    header = {"application-type": '1', "authorization": f"{authorization}", "orgid": f"{orgid}",
              "endpointtype": "1"}
    return header


if __name__ == '__main__':
    del_org_header('1', '2').pr
