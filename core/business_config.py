from dataclasses import dataclass, field


@dataclass(frozen=True)
class DefRules:
    accepted_status: str = "DATOS BANCARIOS"
    bcp_name: str = "BANCO DE CREDITO DEL PERU"
    bcp_aliases: tuple[str, ...] = ("BANCO CENTRAL RESERVA DEL PERU",)
    unusual_amount: float = 1500.0


@dataclass(frozen=True)
class CommercialRules:
    currency_aliases: dict[str, str] = field(
        default_factory=lambda: {
            "SOL": "S/",
            "SOLES": "S/",
            "S/.": "S/",
            "S": "S/",
            "S/": "S/",
            "DOL": "US$",
            "DOLAR": "US$",
            "DOLARES": "US$",
            "$": "US$",
            "USD": "US$",
            "US$": "US$",
        }
    )
    account_by_currency: dict[str, str] = field(
        default_factory=lambda: {"S/": "121210170", "US$": "121210230"}
    )
    detraction_threshold_pen: float = 700.0
    detraction_rate: float = 0.12
    detraction_code: str = "022"
    due_days: int = 30
    folio_prefix: str = "F001"
    series: str = "161"
    payment_group_code: str = "18"
    service_code: str = "SV0004"
    revenue_account: str = "759600000"
    costing_code: str = "A0202000"
    tax_code: str = "IGV_18"
