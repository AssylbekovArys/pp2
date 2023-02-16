def solve(numheads, numlegs):
    ch = 0
    rab = 0
    ch = (4*numheads - numlegs)/2
    rab = numheads - ch
    return {"chickens": ch, "rabbits": rab}
print(solve(35,92))