def aggregate_gradients(gradients):
    # Взвешенное федеративное усреднение
    aggregated = []
    for layer in zip(*gradients):
        aggregated.append(sum(layer) / len(layer))
    return aggregated