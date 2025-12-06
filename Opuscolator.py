from flask import Flask, request, jsonify
import pulp

app = Flask(__name__)

def solve_for_N(y, N):
    model = pulp.LpProblem(f"BookletGrouping_N{N}", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{i}", 5, 10, cat="Integer") for i in range(N)]
    z = [[pulp.LpVariable(f"z_{i}_{j}", lowBound=0) for j in range(N)] for i in range(N)]

    for i in range(N):
        for j in range(N):
            model += z[i][j] >= x[i] - x[j]
            model += z[i][j] >= x[j] - x[i]

    if N > 1:
        model += pulp.lpSum([z[i][j]/2 for i in range(N) for j in range(N)]) / (N*(N-1))
    else:
        model += 0

    model += 4 * pulp.lpSum(x) == y
    model.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[model.status] == "Optimal":
        xi_values = [int(v.value()) for v in x]
        obj_val = pulp.value(model.objective)
        return xi_values, obj_val
    else:
        return None, None

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    y = data['total_pages']
    N_min = (y + 39)//40
    N_max = y//20
    results = []

    for N in range(N_min, N_max + 1):
        xi_values, obj_val = solve_for_N(y, N)
        if xi_values is not None:
            results.append({
                'N': N,
                'xi_values': xi_values,
                'obj_val': obj_val
            })

    return jsonify({'result': results})

if __name__ == '__main__':
    app.run(debug=True)
