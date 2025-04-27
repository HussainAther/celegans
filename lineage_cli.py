import argparse
from build_initial_lineage import build_lineage_tree, add_random_syncytial_cells
from fate_utils import assign_cell_fates
from lineage_visualizer import visualize_lineage_tree
from export_utils import export_lineage_graphml, export_lineage_json
from animate_lineage import animate_lineage_by_time

def main():
    parser = argparse.ArgumentParser(description="🧬 C. elegans Lineage CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Visualize Command
    vis_parser = subparsers.add_parser('visualize', help="Visualize the lineage tree")
    vis_parser.add_argument('--fate', action='store_true', help="Color by cell fate")
    vis_parser.add_argument('--save', type=str, help="Path to save image (e.g., tree.png)")
    vis_parser.add_argument('--show', action='store_true', help="Display the plot")

    # Export Command
    export_parser = subparsers.add_parser('export', help="Export the lineage tree")
    export_parser.add_argument('--format', choices=['graphml', 'json'], required=True)
    export_parser.add_argument('--output', type=str, required=True, help="Output filename")

    # Animate Command
    anim_parser = subparsers.add_parser('animate', help="Animate lineage by division time")
    anim_parser.add_argument('--output', type=str, default="lineage.gif", help="Output GIF filename")
    anim_parser.add_argument('--speed', type=float, default=0.8, help="Frame duration in seconds")

    args = parser.parse_args()

    # Build and annotate lineage
    lineage_tree = build_lineage_tree()
    add_random_syncytial_cells(lineage_tree, num_cells=10)
    assign_cell_fates(lineage_tree)

    # Handle commands
    if args.command == "visualize":
        visualize_lineage_tree(lineage_tree, color_by_fate=args.fate, save_path=args.save, show=args.show)

    elif args.command == "export":
        if args.format == "graphml":
            export_lineage_graphml(lineage_tree, filename=args.output)
        elif args.format == "json":
            export_lineage_json(lineage_tree, filename=args.output)

    elif args.command == "animate":
        animate_lineage_by_time(lineage_tree, output_gif=args.output, frame_duration=args.speed)


if __name__ == "__main__":
    main()

