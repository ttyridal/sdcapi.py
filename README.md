# No longer works

See issue #2  - The backend api has introduced a requirement for device registration. One step in that
registration is Google SafetyNet attestation. I have no plans on trying to circumvent that one. (Furthermore,
in the event that a loophole is found, it would likely be closed by google very fast)

# PSD2
Back in 2018 I was (young and foolishly) hoping that PSD2 would soon make this obsolete anyway.. Now, 4 years
later that's clearly not the case. Yes, most (all?) banks have PSD2 API's, but personal access to these or other
are few and far between.

PSD2 turned out to be "pay to play" (EV-type certificates) and well guarded agaist personal use with government license requirements etc.
In short the whole PSD2 story looks like a huge failure in the eyes of personal developers eying an opportunity to
analyze their own data or develop a small scale app.

As I see it, the only remaining opportunity is to let your voice be heard! Poke your bank and demand API access for personal use!



# SDC Mobile Banking API client

This is a python client library to access the banking api of [SDC](http://sdc.dk).
SDC is a service provider for multiple banks, listed below.

The api was reversed from (one of) the mobile app(s).

To use the api, you'll need the bank identifier for the bank in question,
see bankidentifiers.pdf, fetched [here](http://www.norges-bank.no/pages/69405/Deltagere_NICS_30_06_2014.pdf)
March, 2016

You may also need to connect to the bank once
with the ordinary app (not tested) first. 

## Disclaimer
This is an unofficial, reverse-engineered, implementation of the api. It is provided "as is" without warranty
of any kind.

Further, your bank or SDC may not approve the use of this software.

## List of banks using SDC
* Aasen Sparebank
* Andebu Sparebank
* Arendal og Omegns Sparekasse
* Askim og Spydeberg Sparebank
* Aurland Sparebank
* Aurskog Sparebank
* Bamble og Langesund Sparebank
* Bank Norwegian
* Bank2
* Berg Sparebank
* Bien Sparebank
* Birkenes Sparebank
* Bjugn Sparebank
* Blaker Sparebank
* Bud, Fræna og Hustad Sparebank
* Cultura
* Drangedal Sparebank
* Eidsberg Sparebank
* Etnedal Sparebank
* Evje og Hornnes Sparebank
* Fornebubanken
* Gildeskål Sparebank
* Gjerstad Sparebank
* Grong Sparebank
* Grue Sparebank
* Haltdalen Sparebank
* Harstad Sparebank
* Hegra Sparebank
* Hjartdal og Gransherad Sparebank
* Hjelmeland Sparebank
* Høland og Setskog Sparebank
* Hønefoss Sparebank
* Indre Sogn Sparebank
* Jernbanepersonalets Sparebank
* Jæren Sparebank
* Klæbu Sparebank
* Kragerø Sparebank
* Kvinesdal Sparebank
* Larvikbanken Brunlanes Sparebank
* LillestrømBanken
* Lofoten Sparebank
* Marker Sparebank
* Meldal Sparebank
* Melhus Sparebank
* Nesset Sparebank
* Odal Sparebank
* Ofoten Sparebank
* Oppdalsbanken
* Orkdal Sparebank
* Personellservice Trøndelag
* Rindal Sparebank
* RørosBanken Røros Sparebank
* Sandnes Sparebank
* Selbu Sparebank
* Skue Sparebank
* Soknedal Sparebank
* Sparebanken DIN
* Sparebanken Hemne
* Sparebanken Narvik
* Stadsbygd Sparebank
* Storebrand
* Strømmen Sparebank
* Sunndal Sparebank
* Surnadal Sparebank
* Tinn Sparebank
* Tolga-Os Sparebank
* Totens Sparebank
* Trøgstad Sparebank
* Tysnes Sparebank
* Valle Sparebank
* Vang Sparebank
* Vegårshei Sparebank
* Vekselbanken
* Verdibanken
* Vestre Slidre Sparebank
* Vik Sparebank
* yA Bank
* Ørland Sparebank
* Ørskog Sparebank
* Åfjord Sparebank
