# LidarI2C
## Projekt obslug Lidaru Lite v3Hp
### W jezyku Python dla Raspberry Pi

Używa biblioteki `smbus2` do obsługi i2c w języky Python

Zaleca sie uzywanie zestawu gotowych narzedzi na raspbery `i2ctools`.

# Konfiguracja
Wyróżniamy następujące możliwości konfiguracji:
- Domyślny
- Wysoka prędkość przy małym zakresie
- wysoka czułość
- niska czułość
- maksymalny zakres
- krótszy zasięg i wysoka prędkość
- jeszcze szybszy, przy większym błędzie i mniejszym zakresie.

# Tryby pracy
Wyrozniamy nastepujace tryby pracy:
- Pojedynczy pomiar
- Ciagle pomiary
- Szybkie pomiary

# TODO

- [x] Utworzyć repo na gicie
- [x] Zaimplementować prosty pojedynczy pomiar
- [X] Zaimplementować mozliwosc konfiguracji i wyboru tryby pracy w wierszu polecen
- [X] Zaimplementować możliwość wielu pomiarów (tryb pracy ciągłej)
- [X] Zaimplementować możliwość pomiarów z zadanym okresem
- [X] Zaimplementować możliwość wychodzenia z programu przy pracy ciągłej
- [ ] Okomentować kod
- [ ] Stworzyć dokumentację
- [ ] Zaimplementować możliwość zmiary adresu I2C lidaru
- [ ] Zaimplentować tryb testowy do badanie wydajności programu + Lidaru (praca ciągła)
