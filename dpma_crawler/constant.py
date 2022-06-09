import enum

BOOTSTRAP_SERVER: str = "localhost:29092"
SCHEMA_REGISTRY_URL: str = "http://localhost:8081"
TOPIC: str = "patent-events"

COOKIE = {
    "pat.checkedList": "Aktenzeichen_Schutzrechtsart_Anmelder_Anmeldetag_Bezeichnung_Eintragungstag_Erfinder_IPCHauptklasse_IPCNebenklassen_Status_Veroeffentlichungsdatum_Vertreter_",
    "pat.ansicht": "tabelle"
}
