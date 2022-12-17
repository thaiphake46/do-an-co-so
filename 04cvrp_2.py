"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = [
        [
            0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
            468, 776, 662
        ],
        [
            548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            320, 1084, 514
        ],
        [
            194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            274, 810, 468
        ],
        [
            536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    ]
    data['demands_weight'] = [0, 1, 1, 2, 4,
                              2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data['demands_volume'] = [0, 2, 2, 4, 8,
                              4, 8, 16, 16, 2, 4, 2, 4, 8, 8, 16, 16]
    data['vehicle_weight'] = [15, 15, 15, 15]
    data['vehicle_volume'] = [30, 30, 30, 30]
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'\nObjective: {solution.ObjectiveValue()}')
    print('---------------------------------------------------------------------------------------')
    total_distance = 0
    total_load = 0
    total_volume = 0

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_load = 0
        route_volume = 0
        str_load = 'Weight:\n\t| '
        str_volume = 'Volume:\n\t| '

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands_weight'][node_index]
            route_volume += data['demands_volume'][node_index]
            str_load += ' {0} Load({1}) -> '.format(node_index, route_load)
            str_volume += ' {0} Volume({1}) -> '.format(node_index,
                                                        route_volume)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)

        str_load += ' {0} Load({1}) |'.format(manager.IndexToNode(index),
                                              route_load)
        str_volume += ' {0} Volume({1}) |'.format(manager.IndexToNode(index),
                                                  route_volume)

        print('Route for vehicle {}:'.format(vehicle_id))
        print('---------------------------------------------------------------------------------------------------------------')
        print(str_load)
        print(str_volume)
        print('Distance of the route: {}m'.format(route_distance))
        print('Load of the route: {}'.format(route_load))
        print('Volume of the route: {}'.format(route_volume))
        print('---------------------------------------------------------------------------------------------------------------')
        total_distance += route_distance
        total_load += route_load
        total_volume += route_volume

    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    print('Total volume of all routes: {}'.format(total_volume))
    print()


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity weight constraint.
    def demand_weight_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands_weight'][from_node]

    demand_weight_callback_index = routing.RegisterUnaryTransitCallback(
        demand_weight_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_weight_callback_index,
        0,  # null capacity slack
        data['vehicle_weight'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity_weight')

    # Add Capacity volume constraint.
    def demands_volume_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands_volume'][from_node]

    demand_volume_callback_index = routing.RegisterUnaryTransitCallback(
        demands_volume_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_volume_callback_index,
        0,  # null capacity slack
        data['vehicle_volume'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity_volume')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    # search_parameters.time_limit.seconds = 5
    search_parameters.time_limit.FromSeconds(5)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("no solution")


if __name__ == '__main__':
    main()
