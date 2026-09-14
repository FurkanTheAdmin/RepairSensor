# Tamir Slotu Doluluk Takibi (HC-SR04 + Raspberry Pi 4)

4 adet HC-SR04 ultrasonik mesafe sensörü ile 4 tamir slotunun doluluğunu izler,
bir araç algılandığında süre saymaya başlar ve durumu bir web sayfasında
canlı olarak gösterir.

## Donanım bağlantısı

Her HC-SR04 için:

- `VCC` -> Pi `5V`
- `GND` -> Pi `GND`
- `TRIG` -> Pi GPIO (doğrudan bağlanabilir, 3.3V mantık seviyesi)
- `ECHO` -> **gerilim bölücü üzerinden** Pi GPIO

**Önemli:** HC-SR04'ün `ECHO` çıkışı 5V'tur, Pi'nin GPIO girişleri ise sadece
3.3V'a dayanıklıdır. `ECHO` hattını doğrudan bağlamak GPIO pinine zamanla
zarar verir. `ECHO` -> GPIO arasına bir direnç gerilim bölücü (örn. 1kΩ ve
2kΩ) koyun (2kΩ ucu GND'ye, ortadan Pi GPIO'ya).

Varsayılan pin eşlemesi ([config.py](config.py) içinde değiştirilebilir):

| Slot | TRIG (BCM) | ECHO (BCM) |
|------|-----------|-----------|
| 1    | 17        | 27        |
| 2    | 22        | 23        |
| 3    | 5         | 6         |
| 4    | 13        | 19        |

## Raspberry Pi ilk kurulum (SSH erişimi olan kişi yapacak)

Trixie'de sistem pip'i "externally managed" olduğu için `gpiozero`/`lgpio`/
`flask` **apt üzerinden** kurulur (pip ile `lgpio` derlemek build-essential +
swig gerektirir, apt paketi bu derlemeyi atlar). Bu yüzden venv gerekmiyor.

```bash
# 0. Paketleri güncelle ve gerekenleri kur
sudo apt update
sudo apt install -y git python3-gpiozero python3-lgpio python3-flask

# 1. GitHub'daki repoyu klonla
git clone https://github.com/FurkanTheAdmin/RepairSensor.git
cd RepairSensor

# 2. Servis olarak kur (arka planda çalışsın, Pi yeniden başlayınca otomatik açılsın)
sudo cp deploy/slot-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now slot-monitor

# 3. Durumu kontrol et
sudo systemctl status slot-monitor
```

Web arayüzü `http://<pi-ip>:8080` adresinde açılır.

Bu depoda `User=rasp` ve `/home/rasp/RepairSensor` kullanıcı adı olarak
`rasp` seçildiği için böyle ayarlandı. Farklı bir kullanıcı adıyla
kuruyorsanız [deploy/slot-monitor.service](deploy/slot-monitor.service)
içindeki `User=` ve `WorkingDirectory=` satırlarını ona göre değiştirin.

## Kod güncellendiğinde Pi'de nasıl "pull" edilir

Siz (bu bilgisayardan) kodu değiştirip GitHub'a `git push` yaptıktan sonra,
Pi'ye SSH erişimi olan kişi şunlardan birini çalıştırır:

**Kısa yol — hazır script:**

```bash
ssh rasp@<pi-ip>
cd /home/rasp/RepairSensor
bash deploy/update.sh
```

Bu script sırasıyla: `git pull` yapar ve `slot-monitor` servisini yeniden
başlatır.

**Manuel adımlar (script kullanmadan aynısı):**

```bash
ssh rasp@<pi-ip>
cd /home/rasp/RepairSensor
git pull
sudo systemctl restart slot-monitor
sudo systemctl status slot-monitor
```

(`requirements.txt`'e yeni bir bağımlılık eklenirse, onu da apt ile
kurmanız gerekir — bkz. yukarıdaki ilk kurulum adımı.)

Not: `git pull` yerel değişiklikler varsa (Pi üzerinde elle bir şey
düzenlendiyse) çakışabilir. Pi'deki kopya sadece deploy hedefi olarak
kullanılmalı, orada elle düzenleme yapılmamalı.

## Yerel geliştirme (bu bilgisayarda, GPIO donanımı olmadan)

Windows/Mac/Linux geliştirme makinesinde gerçek donanım olmadan Flask
uygulamasını (mock sensörlerle) çalıştırmak için:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install flask gpiozero
set GPIOZERO_PIN_FACTORY=mock   # Windows cmd; bash: export GPIOZERO_PIN_FACTORY=mock
python app.py
```

(`lgpio` gerçek donanım gerektirdiği için geliştirme makinesine kurulması
gerekmez; `mock` pin factory ile sadece web arayüzü/akış test edilir, mesafe
değerleri gerçek olmaz.)

## Ayarlar

[config.py](config.py) içindeki varsayılanlar, aynı isimde bir ortam
değişkeniyle kod değiştirmeden override edilebilir. En pratik yol,
[deploy/slot-monitor.service](deploy/slot-monitor.service) içindeki
`Environment=` satırlarını düzenleyip şunu çalıştırmak:

```bash
sudo systemctl daemon-reload
sudo systemctl restart slot-monitor
```

- `OCCUPIED_THRESHOLD_M`: bu mesafenin altı "araç var" sayılır (varsayılan 0.5m / 50cm)
- `CONFIRM_SECONDS`: aracın sayaç başlamadan önce eşiğin altında **kesintisiz** kaç saniye görülmesi gerektiği (varsayılan 20s) — kısa süreli geçişleri (biri önünden yürüyüp geçmesi gibi) filtreler
- `EXIT_CONFIRM_SECONDS`: slot boşaldığında sayacın sıfırlanması için aracın eşiğin dışında kesintisiz kaç saniye görülmesi gerektiği (varsayılan 2s) — tek karelik ölçüm gürültüsünü filtreler
- `HISTORY_SIZE`: her slotun altında kaç geçmiş tamir süresinin tutulup gösterileceği (varsayılan 3) — bu geçmiş bellekte tutulur, servis yeniden başlarsa sıfırlanır
- `POLL_INTERVAL_S`: sensörlerin ne sıklıkla okunacağı
- `MAX_DISTANCE_M`: bu mesafenin üzerindeki okumalar geçersiz sayılır
