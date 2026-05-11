def interpret_business(driver_result, relationships):
    if not driver_result:
        return None

    driver = driver_result["driver"]
    target = driver_result["target"]

    return (
        f"{target} büyük ölçüde {driver} tarafından belirleniyor. "
        f"Bu, {driver} süresinin artırılmasının doğrudan {target} üzerinde etkili olacağını gösterir."
    )