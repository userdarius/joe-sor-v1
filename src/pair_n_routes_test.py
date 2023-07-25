import src.main as main

# Create some pairs (for demonstration purposes)
pair1 = pair.copy()  # Make a copy so we can modify it without affecting the original
pair1["pairAddress"] = "address1"
pair1["tokenX"] = "token1"
pair1["tokenY"] = "token2"

pair2 = pair.copy()  # Make a copy so we can modify it without affecting the original
pair2["pairAddress"] = "address2"
pair2["tokenX"] = "token3"
pair2["tokenY"] = "token4"

# Add these pairs to the route
route["pairs"].append(pair1)
route["pairs"].append(pair2)

# Now the route dictionary contains a list of pairs
print(route)
