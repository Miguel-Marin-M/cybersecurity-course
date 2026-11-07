import nmap

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

def show_results(scanner):
    if scanner is None:
        print("No se pudo completar el escaneo.")
        return

    for host in scanner.all_hosts():
        print(f"\nHost: {host}")
        print(f"Estado: {scanner[host].state()}")

        for proto in scanner[host].all_protocols():
            print(f"\nProtocolo: {proto}")
            puertos = scanner[host][proto].keys()
            for puerto in puertos:
                info = scanner[host][proto][puerto]
                print(f"  Puerto {puerto}: {info['state']} - {info['name']} {info['product']} {info['version']}")

if __name__ == "__main__":
    target_ip = input("IP a escanear: ")
    result = scan(target_ip)
    show_results(result)
