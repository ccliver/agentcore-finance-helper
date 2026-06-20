def compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
    additional_monthly: float = 0.0,
) -> dict:
    rate = annual_rate / 100
    n = compounds_per_year

    principal_balance = principal * (1 + rate / n) ** (n * years)

    contributions_balance = 0.0
    if additional_monthly:
        monthly_rate = (1 + rate / n) ** (n / 12) - 1
        months = years * 12
        if monthly_rate:
            contributions_balance = additional_monthly * (
                ((1 + monthly_rate) ** months - 1) / monthly_rate
            )
        else:
            contributions_balance = additional_monthly * months

    final_balance = principal_balance + contributions_balance
    total_contributed = principal + additional_monthly * 12 * years

    return {
        "final_balance": round(final_balance, 2),
        "total_interest": round(final_balance - total_contributed, 2),
        "principal": principal,
        "total_contributed": round(total_contributed, 2),
        "years": years,
    }


def loan_payment(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
) -> dict:
    monthly_rate = (1 + annual_rate / 100 / compounds_per_year) ** (compounds_per_year / 12) - 1
    months = years * 12

    if monthly_rate:
        monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)
    else:
        monthly_payment = principal / months

    total_paid = monthly_payment * months

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_paid - principal, 2),
        "principal": principal,
        "years": years,
    }


TOOLS = {
    "compound_interest": compound_interest,
    "loan_payment": loan_payment,
}


def lambda_handler(event, context):
    full_name = context.client_context.custom["bedrockAgentCoreToolName"]
    tool_name = full_name[full_name.index("___") + 3:]
    return TOOLS[tool_name](**event)
