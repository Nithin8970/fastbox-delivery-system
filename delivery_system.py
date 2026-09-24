import json
import math
import csv
from pathlib import Path


def load_data(file_path):
    """Read and parse the JSON input file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_data(data):
    """
    Support both the PDF format and the supplied base_case format.

    PDF:
        warehouses: {"W1": [x, y], ...}
        agents: {"A1": [x, y], ...}
        package key: "warehouse"

    Supplied base_case:
        warehouses: [{"id": "W1", "location": [x, y]}, ...]
        agents: [{"id": "A1", "location": [x, y]}, ...]
        package key: "warehouse_id"
    """
    if isinstance(data["warehouses"], list):
        warehouses = {
            item["id"]: item["location"]
            for item in data["warehouses"]
        }
    else:
        warehouses = data["warehouses"]

    if isinstance(data["agents"], list):
        agents = {
            item["id"]: item["location"]
            for item in data["agents"]
        }
    else:
        agents = data["agents"]

    packages = []
    for package in data["packages"]:
        normalized = dict(package)
        if "warehouse" not in normalized and "warehouse_id" in normalized:
            normalized["warehouse"] = normalized["warehouse_id"]
        packages.append(normalized)

    return {
        "warehouses": warehouses,
        "agents": agents,
        "packages": packages,
    }


def euclidean_distance(point_a, point_b):
    """Calculate Euclidean distance between two [x, y] coordinates."""
    return math.sqrt(
        (point_a[0] - point_b[0]) ** 2
        + (point_a[1] - point_b[1]) ** 2
    )


def assign_packages(data):
    """Assign each package to the nearest agent from the warehouse."""
    assignments = {agent_id: [] for agent_id in data["agents"]}

    for package in data["packages"]:
        warehouse_location = data["warehouses"][package["warehouse"]]

        nearest_agent = min(
            data["agents"],
            key=lambda agent_id: euclidean_distance(
                data["agents"][agent_id], warehouse_location
            )
        )

        assignments[nearest_agent].append(package)

    return assignments


def simulate_delivery(data, assignments):
    """
    For each assigned package:
        current location -> warehouse -> destination

    After delivery, the agent's current location becomes the destination.
    No return trip is assumed because the task does not request one.
    """
    report = {}
    route_details = {}

    for agent_id, packages in assignments.items():
        current_location = data["agents"][agent_id]
        total_distance = 0.0
        delivered = []

        for package in packages:
            warehouse_location = data["warehouses"][package["warehouse"]]
            destination = package["destination"]

            to_warehouse = euclidean_distance(
                current_location, warehouse_location
            )
            to_destination = euclidean_distance(
                warehouse_location, destination
            )

            package_distance = to_warehouse + to_destination
            total_distance += package_distance

            delivered.append({
                "package_id": package["id"],
                "warehouse": package["warehouse"],
                "destination": destination,
                "distance_to_warehouse": round(to_warehouse, 2),
                "distance_warehouse_to_destination": round(to_destination, 2),
                "total_package_distance": round(package_distance, 2),
            })

            current_location = destination

        count = len(packages)
        efficiency = total_distance / count if count else 0.0

        report[agent_id] = {
            "packages_delivered": count,
            "total_distance": round(total_distance, 2),
            "efficiency": round(efficiency, 2),
        }
        route_details[agent_id] = delivered

    active_agents = [
        agent_id for agent_id, info in report.items()
        if info["packages_delivered"] > 0
    ]

    best_agent = (
        min(active_agents, key=lambda x: report[x]["efficiency"])
        if active_agents else None
    )

    return report, route_details, best_agent


def save_report(report, route_details, best_agent, output_file):
    """Save the final report to JSON."""
    result = {**report, "best_agent": best_agent, "route_details": route_details}

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)


def export_top_performer_csv(report, best_agent, output_file):
    """Bonus: export the best agent to CSV."""
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "agent_id", "packages_delivered",
            "total_distance", "efficiency"
        ])

        if best_agent:
            info = report[best_agent]
            writer.writerow([
                best_agent,
                info["packages_delivered"],
                info["total_distance"],
                info["efficiency"],
            ])


def print_report(report, best_agent):
    print("\nFASTBOX DELIVERY REPORT")
    print("-" * 55)

    for agent_id, info in report.items():
        print(
            f"{agent_id}: packages={info['packages_delivered']}, "
            f"distance={info['total_distance']:.2f}, "
            f"efficiency={info['efficiency']:.2f}"
        )

    print("-" * 55)
    print(f"Best agent: {best_agent}")


def main():
    input_file = Path("data.json")
    report_file = Path("report.json")
    csv_file = Path("top_performer.csv")

    raw_data = load_data(input_file)
    data = normalize_data(raw_data)

    assignments = assign_packages(data)

    assigned_count = sum(len(items) for items in assignments.values())
    if assigned_count != len(data["packages"]):
        raise ValueError("Not all packages were assigned.")

    report, route_details, best_agent = simulate_delivery(
        data, assignments
    )

    save_report(report, route_details, best_agent, report_file)
    export_top_performer_csv(report, best_agent, csv_file)
    print_report(report, best_agent)


if __name__ == "__main__":
    main()
