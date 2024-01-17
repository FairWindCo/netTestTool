import requests
from requests_ntlm2 import HttpNtlmAuth

from clients.patch_dns_util import dns_service_control

if __name__ == "__main__":
    session = requests.Session()
    dns_service_control.activate_rules({
        "common.sites.local.erc": "10.225.24.64",
    })
    session.auth = HttpNtlmAuth('erc\\cwrk_ShipmentOrder', 'Q/a7GoUb]uA1')
    session.proxies = {
        'http':'',
        'https':''
    }
    res = session.post(url="https://common.sites.local.erc/api/TaxInvoice/TaxInvoiceSaveXmlAndConfirm", verify=False,
                       json={
                           "isNeedExport": True,
                           "who": "erc\samoilov",
                           "docId": 48202848,
                           "docStatusId": 74,
                           "isTaxInvoice": False,
                           "isElectronic": False

                       })
    print(res)
    print(res.text)