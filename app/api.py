# -*- coding: utf-8 -*-
"""
A simple class for accessing the API of the Marktstammdatenregister.

To use this class, you must first register as a Webdienstnutzer/Marktakteur on
the Marktstammdatenregister website:
    https://test.marktstammdatenregister.de/MaStR

Once you have registered, you will receive a marktakteurMastrNummer and an
apiKey, which you can use to access the API.

Overview
https://www.marktstammdatenregister.de/MaStRHilfe/files/webdienst/Funktionen_MaStR_Webdienste_V24.2.139.html
"""

from datetime import date, datetime
from typing import Any

from zeep import Client, Settings, Transport
from zeep.cache import SqliteCache
from zeep.helpers import serialize_object

from app.enums import (
    AnlagenBetriebsStatus,
    BrennstoffLage,
    BundeslaenderEinheiten,
    EEGEinheiten,
    Einheiten,
    Energietraeger,
    Marktfunktion,
    Marktrollen,
    Regelzone,
    ServicePort,
    Spannungsebene,
    TechnologieVerbrennungsanlage,
)


class NotAuthorizedError(Exception):
    """Raise when the user is not authorized to access the API."""


class _MaStR_Base:
    API_ENDPOINT = "https://www.marktstammdatenregister.de/MaStRAPI/wsdl/mastr.wsdl"

    def __init__(self):
        self.api_key: str | None = None
        self.marktakteur_nummer: str | None = None

        transport = Transport(cache=SqliteCache())
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(wsdl=self.API_ENDPOINT, transport=transport, settings=settings)

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def set_marktakteur_nummer(self, marktakteur_nummer: str) -> None:
        self.marktakteur_nummer = marktakteur_nummer

    def get(
        self,
        service_port: ServicePort,
        method_name: str,
        **kwargs,
    ) -> dict[str, Any]:
        # Bind to the requested port
        client_bind = self.client.bind("Marktstammdatenregister", service_port.value)
        method = getattr(client_bind, method_name)

        # Add the API key and marktakteur number to the keyword arguments if they are set
        if self.api_key:
            kwargs["apiKey"] = self.api_key
        if self.marktakteur_nummer:
            kwargs["marktakteurMastrNummer"] = self.marktakteur_nummer

        # Call the SOAP method
        data = method(**kwargs)
        return serialize_object(data)


class MaStR(_MaStR_Base):
    def test_connection(self) -> dict[str, Any]:
        """Test the connection to the Marktstammdatenregister API."""
        return self.get(ServicePort.ALLGEMEIN, "GetLokaleUhrzeit")

    def test_authorization(self) -> dict[str, Any]:
        """Test if the api key is valid to access the Marktstammdatenregister API."""
        if not self.api_key:
            raise NotAuthorizedError("API key is not set.")
        return self.get(ServicePort.ALLGEMEIN, "GetLokaleUhrzeitMitAuthentifizierung")

    def get_eeg_unit(self, unit_type: EEGEinheiten, unit_number: str) -> dict[str, Any]:
        """
        Get data of power units from the Marktstammdatenregister API.

        Parameters
        ----------
        unit_type: EEGEinheiten
            Value of the enum `EEGEinheiten`.
        unit_number: str
            The MaStR number of the desired EEG unit.

        Returns
        -------
        dict[str, Any]
            The data returned by the API method, serialized as a dictionary.
        """
        if not self.api_key or not self.marktakteur_nummer:
            raise NotAuthorizedError("API key or Marktakteur number is not set.")
        return self.get(ServicePort.ANLAGE, unit_type.value, eegMastrNummer=unit_number)

    def get_unit(self, unit_type: Einheiten, unit_number: str) -> dict[str, Any]:
        """
        Get data of power units from the Marktstammdatenregister API.

        Parameters
        ----------
        unit_type: Einheiten
            Value of the enum `Einheiten`.
        unit_number: str
            The MaStR number of the desired unit.

        Returns
        -------
        dict[str, Any]
            The data returned by the API method, serialized as a dictionary.
        """
        if not self.api_key or not self.marktakteur_nummer:
            raise NotAuthorizedError("API key or Marktakteur number is not set.")
        return self.get(ServicePort.ANLAGE, unit_type.value, einheitMastrNummer=unit_number)

    def get_player(self, mastr_nummer: str, **kwargs: dict[str, str]) -> dict[str, Any]:
        """
        Get information about a market player from the Marktstammdatenregister API.

        Parameters
        ----------
        mastr_nummer : str
            The MaStR number of the market player.
        **kwargs : dict[str, str]
            Additional keyword arguments to pass to the API method.

        Returns
        -------
        dict[str, Any]
            The data returned by the API method, serialized as a dictionary.
        """
        if not self.api_key or not self.marktakteur_nummer:
            raise NotAuthorizedError("API key or Marktakteur number is not set.")
        return self.get(ServicePort.AKTEUR, "GetMarktakteur", mastrNummer=mastr_nummer, **kwargs)

    def get_units(
        self,
        startAb: int | None = None,
        datumAb: datetime | None = None,
        limit: int | None = None,
        einheitBetriebsstatus: AnlagenBetriebsStatus | None = None,
        name: str | None = None,
        energietraeger: Energietraeger | None = None,
        postleitzahl: str | None = None,
        ort: str | None = None,
        einheitBundesland: BundeslaenderEinheiten | None = None,
        bruttoleistung: float | None = None,
        bruttoleistungKleiner: float | None = None,
        bruttoleistungGroesser: float | None = None,
        nettoleistung: float | None = None,
        nettoleistungKleiner: float | None = None,
        nettoleistungGroesser: float | None = None,
        hauptbrennstoff: BrennstoffLage | None = None,
        inbetriebnahmedatum: date | None = None,
        inbetriebnahmedatumKleiner: date | None = None,
        inbetriebnahmedatumGroesser: date | None = None,
        technologie: TechnologieVerbrennungsanlage | None = None,
        lokationNetzbetreiber: str | None = None,
        lokationSpannungsebene: Spannungsebene | None = None,
        eegInbetriebnahmedatum: date | None = None,
        eegInbetriebnahmedatumKleiner: date | None = None,
        eegInbetriebnahmedatumGroesser: date | None = None,
        zuschlagsnummer: str | None = None,
        speicherNutzbareSpeicherkapazität: float | None = None,
        speicherNutzbareSpeicherkapazitätKleiner: float | None = None,
        speicherNutzbareSpeicherkapazitätGroesser: float | None = None,
        Registrierungsdatum: date | None = None,
        RegistrierungsdatumKleiner: date | None = None,
        RegistrierungsdatumGroesser: date | None = None,
        netzRegelzone: Regelzone | None = None,
        AnlagenbetreiberMastrNummer: str | None = None,
    ) -> dict[str, Any]:
        """Get data of power units from the Marktstammdatenregister API."""
        if not self.api_key or not self.marktakteur_nummer:
            raise NotAuthorizedError("API key or Marktakteur number is not set.")
        return self.get(
            ServicePort.ANLAGE,
            "GetGefilterteListeStromErzeuger",
            startAb=startAb,
            datumAb=datumAb,
            limit=limit,
            einheitBetriebsstatus=einheitBetriebsstatus,
            name=name,
            energietraeger=energietraeger,
            postleitzahl=postleitzahl,
            ort=ort,
            einheitBundesland=einheitBundesland,
            bruttoleistung=bruttoleistung,
            bruttoleistungKleiner=bruttoleistungKleiner,
            bruttoleistungGroesser=bruttoleistungGroesser,
            nettoleistung=nettoleistung,
            nettoleistungKleiner=nettoleistungKleiner,
            nettoleistungGroesser=nettoleistungGroesser,
            hauptbrennstoff=hauptbrennstoff,
            inbetriebnahmedatum=inbetriebnahmedatum,
            inbetriebnahmedatumKleiner=inbetriebnahmedatumKleiner,
            inbetriebnahmedatumGroesser=inbetriebnahmedatumGroesser,
            technologie=technologie,
            lokationNetzbetreiber=lokationNetzbetreiber,
            lokationSpannungsebene=lokationSpannungsebene,
            eegInbetriebnahmedatum=eegInbetriebnahmedatum,
            eegInbetriebnahmedatumKleiner=eegInbetriebnahmedatumKleiner,
            eegInbetriebnahmedatumGroesser=eegInbetriebnahmedatumGroesser,
            zuschlagsnummer=zuschlagsnummer,
            speicherNutzbareSpeicherkapazität=speicherNutzbareSpeicherkapazität,
            speicherNutzbareSpeicherkapazitätKleiner=speicherNutzbareSpeicherkapazitätKleiner,
            speicherNutzbareSpeicherkapazitätGroesser=speicherNutzbareSpeicherkapazitätGroesser,
            Registrierungsdatum=Registrierungsdatum,
            RegistrierungsdatumKleiner=RegistrierungsdatumKleiner,
            RegistrierungsdatumGroesser=RegistrierungsdatumGroesser,
            netzRegelzone=netzRegelzone,
            AnlagenbetreiberMastrNummer=AnlagenbetreiberMastrNummer,
        )

    def get_players(
        self,
        startAb: int | None = None,
        datumAb: datetime | None = None,
        limit: int | None = None,
        name: str | None = None,
        postleitzahl: str | None = None,
        ort: str | None = None,
        bundesland: BundeslaenderEinheiten | None = None,
        marktfunktion: Marktfunktion | None = None,
        Marktrollen: Marktrollen | list[Marktrollen] | None = None,
        MarktrolleMastrNummerIds: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Get data of market players from the Marktstammdatenregister API."""
        if not self.api_key or not self.marktakteur_nummer:
            raise NotAuthorizedError("API key or Marktakteur number is not set.")
        return self.get(
            ServicePort.AKTEUR,
            "GetGefilterteListeMarktakteure",
            startAb=startAb,
            datumAb=datumAb,
            limit=limit,
            name=name,
            postleitzahl=postleitzahl,
            ort=ort,
            bundesland=bundesland,
            marktfunktion=marktfunktion,
            Marktrollen=Marktrollen,
            MarktrolleMastrNummerIds=MarktrolleMastrNummerIds,
        )
