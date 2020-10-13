import json
import os
import shutil
from os import path
from datetime import date
import socket
from win10toast import ToastNotifier
from shutil import copytree,copy2
import sys

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

temp=0

ilosc_lokalna = 0
ilosc_aktualizacja = 0

f = open('config.json', 'r+')

uzytkownicy = json.load(f)

for j in uzytkownicy['globalne']:
   pass

def progressBar(current, total, barLength = 50):
    percent = float(current) * 100 / total
    arrow   = '█' * int(percent/100 * barLength)
    spaces  = '░' * (barLength - len(arrow))

    print('Postęp: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

def copy2_licznik(src,dst):
    global temp
    global ilosc
    if copy2(src,dst):
        temp=temp+1
        #print_percent_done(temp,ilosc)
        progressBar(temp,ilosc)

def copytree(src, dst, symlinks=False, ignore=None):
   for item in os.listdir(src):
       s = os.path.join(src, item)
       d = os.path.join(dst, item)
       if os.path.isdir(s):
          shutil.copytree(s, d, symlinks, ignore, copy_function=copy2_licznik)
       else:
#          shutil.copy2(s, d)
           copy2_licznik(s, d)

def mergefolders(root_src_dir, root_dst_dir):
   for src_dir, dirs, files in os.walk(root_src_dir):
       dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
       if not os.path.exists(dst_dir):
           os.makedirs(dst_dir)
       for file_ in files:
           src_file = os.path.join(src_dir, file_)
           dst_file = os.path.join(dst_dir, file_)
           if os.path.exists(dst_file):
               os.remove(dst_file)
#           shutil.copy(src_file, dst_dir)
           copy2_licznik(src_file, dst_dir)

def powiadomienie(tytul, tresc):
    toast = ToastNotifier()
    toast.show_toast(tytul, tresc, icon_path=None)

def aktualizacja(program):

   global temp
   temp = 0
   global ilosc_aktualizacja
   global ilosc_lokalna
   global ilosc
   nazwa = date.today().strftime("%d-%m-%Y")

   if host_ip == i["adres_ip"]:  # identyfikacja hosta z plikiem konfiguracyjnym po adresie ip

       if i["aktualizacja_%s" % program] == 1:  # sprawdzenie czy program ma sie zaktualizowac 1=tak !1=nie w pliku konfiguracyjnym
           sciezka_globalna = j["sciezka_do_%s_globalna" % program]
           sciezka_uzytkownika = i["sciezka_do_%s_lokalna" % program]
           sciezka_aktualizacja = j["sciezka_do_%s_aktualizacja" % program]
           sciezka = ''
           ilosc_aktualizacja = sum([len(files) for r, d, files in os.walk(sciezka_aktualizacja)])

           if sciezka_uzytkownika == 0:  # jesli sciezka programu w uzytkowniku jest pusta czyli rowna 0 to uzywa sciezki globalnej
               sciezka = sciezka_globalna
           else:
               sciezka = sciezka_uzytkownika
           ilosc_lokalna = sum([len(files) for r, d, files in os.walk(sciezka)])
           if os.path.exists(sciezka) != 1:  # tworzy katalog z programem jesli została zlecona aktualizacja a nie bylo programu

               powiadomienie("Aktualizacja", 'Rozpoczęto tworzenie %s. Proszę czekać...' % (program))
               # -------------------------------------------------------------------------------------------------------------------------------
               print("⏳ Rozpoczeto tworzenie %s [1/1]"%program )
               os.mkdir(sciezka)
               ilosc=ilosc_aktualizacja
               copytree(sciezka_aktualizacja, sciezka)
               print("\n✅ Utworzono %s"%program)

               i["data_ostatniej_aktualizacji_%s" % program] = nazwa
               # ------------------------------------------------------------------------------------------------------------------------------------
               powiadomienie("Aktualizacja", 'Utworzono %s.' % (program))

           else:  # aktualizuje program jeśli już istnieje
               powiadomienie("Aktualizacja", 'Rozpoczęto aktualizację %s. Proszę czekać...' % (program))
               # -------------------------------------------------------------------------------------------------------------------------------
               if path.exists(sciezka + '_%s' % i["data_ostatniej_aktualizacji_%s" % program]): #usuwa poprzednią zapisaną kopię
                   shutil.rmtree(sciezka + '_%s' % i["data_ostatniej_aktualizacji_%s" % program])
               os.rename(sciezka, sciezka + '_%s' % nazwa)  # tworzenie kopii starszej wersji
               os.mkdir(sciezka)
               ilosc=ilosc_lokalna
               print("⏳ Rozpoczęto tworzenie kopii zapasowej %s [1/2]" % program)
               copytree(sciezka + '_%s' % nazwa, sciezka)
               print("\n✅ Utworzono kopię zapasową %s"%program)
               temp=0
               ilosc=ilosc_aktualizacja
               print("⏳ Rozpoczęto aktualizację %s [2/2]"%program)
               mergefolders(sciezka_aktualizacja, sciezka)
               print("\n✅ Zaktualizowano %s"%program)
               temp=0

               i["data_ostatniej_aktualizacji_%s" % program] = nazwa
               # -------------------------------------------------------------------------------------------------------------------------------
               powiadomienie("Aktualizacja", 'Zaktualizowano %s.' % (program))

for i in uzytkownicy['uzytkownicy']:
   for x in uzytkownicy['programy']:
       aktualizacja(x)
print("Pomyślnie wykonano wszystkie operacje")

# print(len(uzytkownicy['programy'][0].keys()))
# print(uzytkownicy['programy'][0]['program_3'])

f = open('config.json', 'w')
json.dump(uzytkownicy, f, indent=2)
f.close()