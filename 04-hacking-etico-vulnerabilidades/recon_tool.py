import nmap
import requests
import time
import sys

def cpe22_to_cpe23(cpe22):
    # cpe:/a:vsftpd:vsftpd:2.3.4  →  cpe:2.3:a:vsftpd:vsftpd:2.3.4:*:*:*:*:*:*:*
    parts = cpe22.replace("cpe:/", "").split(":")
    parts = parts[:4]

    if len(parts) < 4:
        return "incomplete"

    names = ["Part", "Vendor", "Product", "Version"]
    for i, p in enumerate(parts):
        if p == "*":
            return names[i]

    cpe23 = "cpe:2.3:" + ":".join(parts) + ":*:*:*:*:*:*:*"
    return cpe23

def search_cves_by_cpe(cpe22, nvd_api_key):
    if not cpe22:
        return [False, "Uso inválido"]

    cpe23 = cpe22_to_cpe23(cpe22)
    
    if cpe23=="Part" or cpe23=="Vendor" or cpe23=="Product" or cpe23=="Version":
        return [False, f"Falta '{cpe23}'"]
    elif cpe23=="incomplete":
        return [False, "Parámetros incompletos"]

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {"cpeName": cpe23, "resultsPerPage": 10}
    headers= {"apiKey": nvd_api_key}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return [False, f"Error buscando CVEs para {cpe23}: {e}"]

    found_cves = []
    for item in data.get("vulnerabilities", []):
        cve_id = item["cve"]["id"]
        found_cves.append(cve_id)

    time.sleep(1)
    return [True,found_cves]

def scan(ip):
    scanner = nmap.PortScanner()
    print(f"Escaneando {ip}...")
    
    # full host and ports scan
    args='-sV -Pn --min-rate 5000 -p- -n'
    
    if "/" in ip:
        print("Opciones:\n1: Descubrimiento de hosts\n2: Escaneo de todos los hosts y sus puertos\n3: Cancelear")

        while True:
            option = input("Elije (Solo pon el número): ")
        
            if option=="1":
                # host discovery
                args='-sn --min-rate 5000 -n'
                break
            elif option=="3":
                return None
            elif option !="2":
                print("Opción inválida")
                
        try:
            scanner.scan(hosts=ip, arguments=args)
        except Exception as e:
            print(f"Error al escanear: {e}")
            return None
    else:
        try:
            scanner.scan(ip, arguments='-sV -Pn --min-rate 5000 -p-')
        except Exception as e:
            print(f"Error al escanear: {e}")
            return None
    return scanner

def show_results(scanner, nvd_api_key):
    if scanner is None:
        print("No se pudo completar el escaneo.")
        return

    for host in scanner.all_hosts():
        print('\n============================\n')
        print(f"  Host: {host}")
        print(f"  Estado: {scanner[host].state()}")

        for proto in scanner[host].all_protocols():
            print("\n-------Protocolo-------\n")
            print(f"  Protocolo: {proto}")
            ports = scanner[host][proto].keys()
            for port in ports:
                print("\n---------------------\n")
                info = scanner[host][proto][port]
                product = info['product']
                version = info['version']
                cpe = info['cpe']
                print(f"  Puerto {port}: {info['state']} - {info['name']} {product} {version}")

                if cpe:
                    print("\n  CVEs:\n")
                    print(f"  Buscando CVEs para {product} {version}...")
                    cves = search_cves_by_cpe(cpe, nvd_api_key)
                    if cves[0] and cves[1]:
                        print(f"  CVEs encontrados: {', '.join(cves[1])}")
                    else:
                        if cves[1]:
                            print(f"  La busqueda falló: {cves[1]}")
                        else:
                            print("  No se encontraton CVEs conocidos")
                else:
                    print("\n  No se puede buscar CVEs, falta CPE")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 recon_tool.py <nvd-api-key>")
        sys.exit(1)

    nvd_api_key = sys.argv[1]
    target_ip = input("IP a escanear: ")
    result = scan(target_ip)
    show_results(result, nvd_api_key)
