#!/usr/bin/env python3
"""
Background Remover CLI - Enhanced version of rembg
Optimized for white-on-white product images with advanced processing modes.
"""

import os
import sys
import click
import yaml
from pathlib import Path
from typing import Optional

from core.batch_processor import BatchProcessor
from core.utils import scan_images


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Background Remover CLI - White Product Edition

    Enhanced background removal with AI + Classical methods,
    white preservation, and intelligent quality control.
    """
    pass


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('-m', '--mode', type=click.Choice(['A', 'B', 'C']), default='A',
              help='Processing mode: A=AI-first (default), B=Classical-first, C=Hybrid')
@click.option('--model', type=click.Choice(['isnet-general', 'u2net', 'u2netp']),
              default='isnet-general',
              help='AI model to use (default: isnet-general)')
@click.option('--no-white-preserve', is_flag=True,
              help='Disable white preservation (not recommended for white products)')
@click.option('--feather', type=int, default=3,
              help='Edge feather radius in pixels (default: 3)')
@click.option('--no-trim', is_flag=True,
              help='Disable automatic trimming')
@click.option('--config', type=click.Path(exists=True),
              help='Path to YAML config file (overrides other options)')
def process(input_path, output_path, mode, model, no_white_preserve,
            feather, no_trim, config):
    """
    Process a single image or folder.

    Examples:

        # Single image with defaults (Mode A, isnet-general)
        bg-remover process input.jpg output.png

        # Folder with Mode C (Hybrid)
        bg-remover process ./images ./output -m C

        # Use u2net model with custom settings
        bg-remover process input.jpg output.png --model u2net --feather 5

        # Use config file
        bg-remover process ./images ./output --config my_config.yaml
    """

    # Load or create config
    if config:
        cfg = load_config(config)
    else:
        cfg = create_config_from_args(mode, model, no_white_preserve, feather, no_trim)

    # Check if input is file or folder
    input_p = Path(input_path)
    output_p = Path(output_path)

    if input_p.is_file():
        # Single file processing
        process_single_file(input_p, output_p, cfg)
    else:
        # Batch processing
        process_folder(input_p, output_p, cfg)


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path())
@click.option('-m', '--mode', type=click.Choice(['A', 'B', 'C']), default='A',
              help='Processing mode (default: A)')
@click.option('--model', type=click.Choice(['isnet-general', 'u2net', 'u2netp']),
              default='isnet-general',
              help='AI model (default: isnet-general)')
@click.option('-r', '--recursive', is_flag=True, default=True,
              help='Scan subfolders recursively')
@click.option('--ext', multiple=True, default=['jpg', 'jpeg', 'png', 'webp'],
              help='File extensions to process (can be specified multiple times)')
@click.option('--workers', type=int, default=None,
              help='Number of worker threads (default: auto)')
@click.option('--config', type=click.Path(exists=True),
              help='Path to YAML config file')
@click.option('--no-csv', is_flag=True,
              help='Disable CSV report generation')
def batch(input_folder, output_folder, mode, model, recursive, ext,
          workers, config, no_csv):
    """
    Batch process an entire folder.

    Examples:

        # Process all images in folder with defaults
        bg-remover batch ./images ./output

        # Non-recursive, only PNG files
        bg-remover batch ./images ./output --no-recursive --ext png

        # Use 4 workers with Mode C
        bg-remover batch ./images ./output -m C --workers 4

        # Use config file
        bg-remover batch ./images ./output --config config.yaml
    """

    # Load or create config
    if config:
        cfg = load_config(config)
    else:
        cfg = create_config_from_args(mode, model, False, 3, False)
        cfg['input']['extensions'] = list(ext)
        cfg['input']['recursive'] = recursive
        if workers:
            cfg['performance']['concurrency'] = workers
        if no_csv:
            cfg['logging']['csv_enabled'] = False

    # Update paths
    cfg['input']['source_folder'] = str(input_folder)
    cfg['output']['output_folder'] = str(output_folder)

    # Process
    process_folder_batch(cfg)


@cli.command()
def list_models():
    """List available AI models and their descriptions."""

    click.echo("\nAvailable AI Models:\n")

    models = [
        {
            'name': 'isnet-general',
            'size': '~176 MB',
            'description': 'Best for product images (Default)',
            'speed': 'Medium'
        },
        {
            'name': 'u2net',
            'size': '~176 MB',
            'description': 'General purpose, good accuracy',
            'speed': 'Medium'
        },
        {
            'name': 'u2netp',
            'size': '~4.7 MB',
            'description': 'Lightweight, faster processing',
            'speed': 'Fast'
        }
    ]

    for m in models:
        click.echo(f"  {m['name']:<20} {m['size']:<12} {m['description']}")
        click.echo(f"  {'':20} {'':12} Speed: {m['speed']}\n")


@cli.command()
def modes():
    """Explain processing modes."""

    click.echo("\nProcessing Modes:\n")

    click.echo("  Mode A: AI-first + Classical Refine (Default)")
    click.echo("    • Best for: Most product images, white-on-white")
    click.echo("    • Process: AI → White preservation → GrabCut refine")
    click.echo("    • Auto-fallback to Hybrid if QC fails\n")

    click.echo("  Mode B: Classical-first + AI Fallback")
    click.echo("    • Best for: Simple backgrounds, faster processing")
    click.echo("    • Process: Classical (Lab + GrabCut) → AI if needed")
    click.echo("    • Good for batch with mostly easy images\n")

    click.echo("  Mode C: Hybrid-merge")
    click.echo("    • Best for: Complex/challenging images, maximum quality")
    click.echo("    • Process: AI + Classical → Intelligent merge")
    click.echo("    • Slowest but most robust\n")


@cli.command()
@click.argument('output_path', type=click.Path())
@click.option('--mode', type=click.Choice(['A', 'B', 'C']), default='A')
@click.option('--model', type=click.Choice(['isnet-general', 'u2net', 'u2netp']),
              default='isnet-general')
def init_config(output_path, mode, model):
    """
    Generate a default config.yaml file.

    Example:
        bg-remover init-config my_config.yaml --mode A --model isnet-general
    """

    cfg = create_default_config()
    cfg['processing']['mode'] = mode
    cfg['model']['ai_model'] = model

    with open(output_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)

    click.echo(f"✓ Config file created: {output_path}")
    click.echo(f"  Mode: {mode}")
    click.echo(f"  Model: {model}")
    click.echo(f"\nEdit the file to customize settings, then use:")
    click.echo(f"  bg-remover process <input> <output> --config {output_path}")


# Helper functions

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_config_from_args(mode, model, no_white_preserve, feather, no_trim):
    """Create config dict from command-line arguments."""
    cfg = create_default_config()
    cfg['processing']['mode'] = mode
    cfg['model']['ai_model'] = model
    cfg['refinement']['white_preservation']['enabled'] = not no_white_preserve
    cfg['refinement']['edge_feather_px'] = feather
    cfg['refinement']['trimming']['enabled'] = not no_trim
    return cfg


def create_default_config():
    """Create default configuration."""
    return {
        'input': {
            'source_folder': '',
            'extensions': ['jpg', 'jpeg', 'png', 'webp'],
            'recursive': True
        },
        'output': {
            'output_folder': '',
            'overwrite_policy': 'disambiguate'
        },
        'processing': {
            'mode': 'A',
            'force_ai_all': False
        },
        'model': {
            'ai_model': 'isnet-general'
        },
        'refinement': {
            'edge_feather_px': 3,
            'grabcut_enabled': True,
            'grabcut_iterations': 4,
            'white_preservation': {
                'enabled': True,
                'hsv_s_threshold': 25,
                'hsv_v_threshold': 220,
                'lab_l_threshold': 85
            },
            'trimming': {
                'enabled': True,
                'safe_margin_px': 3
            }
        },
        'qc': {
            'fg_ratio_min': 10,
            'fg_ratio_max': 90,
            'edge_confidence_min': 14,
            'fallback_fg_ratio_min': 8,
            'fallback_fg_ratio_max': 95,
            'fallback_edge_confidence_min': 12
        },
        'logging': {
            'csv_enabled': True,
            'debug_masks_enabled': False
        },
        'performance': {
            'concurrency': 'auto',
            'max_side_px': 1800,
            'timeout_ai_ms': 12000,
            'timeout_classical_ms': 4000,
            'queue_order': 'natural'
        }
    }


def process_single_file(input_path, output_path, config):
    """Process a single image file."""
    from core.processor import ImageProcessor
    from core.utils import save_rgba, load_image_bgr
    import time

    click.echo(f"\nProcessing: {input_path.name}")
    click.echo(f"Mode: {config['processing']['mode']}")
    click.echo(f"Model: {config['model']['ai_model']}\n")

    processor = ImageProcessor(config)

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with click.progressbar(length=100, label='Processing') as bar:
        result = processor.process_image(str(input_path), str(output_path.parent))
        bar.update(100)

    if result['status'] == 'success':
        click.echo(f"\n✓ Success!")
        click.echo(f"  Output: {result['output_path']}")
        click.echo(f"  FG Ratio: {result['fg_ratio']:.1f}%")
        click.echo(f"  Edge Conf: {result['edge_conf']:.1f}")
        click.echo(f"  Time: {result['elapsed_ms']}ms")
        if result['notes']:
            click.echo(f"  Notes: {result['notes']}")
    else:
        click.echo(f"\n✖ Failed: {result['notes']}", err=True)
        sys.exit(1)


def process_folder(input_path, output_path, config):
    """Process folder with simple progress."""
    config['input']['source_folder'] = str(input_path)
    config['output']['output_folder'] = str(output_path)
    process_folder_batch(config)


def process_folder_batch(config):
    """Process folder in batch mode with progress bar."""
    from tqdm import tqdm

    input_folder = config['input']['source_folder']
    output_folder = config['output']['output_folder']

    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Scan files
    click.echo(f"\nScanning: {input_folder}")
    files = scan_images(
        input_folder,
        config['input']['extensions'],
        config['input']['recursive']
    )

    if not files:
        click.echo("✖ No images found!", err=True)
        sys.exit(1)

    click.echo(f"Found {len(files)} image(s)")
    click.echo(f"Mode: {config['processing']['mode']}")
    click.echo(f"Model: {config['model']['ai_model']}")
    click.echo(f"Output: {output_folder}\n")

    # Process with progress bar
    processor = BatchProcessor(config)

    progress_bar = tqdm(total=len(files), desc="Processing", unit="img")

    def progress_callback(current, total, message):
        progress_bar.update(1)
        # Extract filename from message
        if '|' in message:
            parts = message.split('|')
            if len(parts) > 1:
                tqdm.write(f"  {parts[0].strip()}: {parts[1].strip()}")

    csv_path = processor.process_batch(
        input_folder,
        output_folder,
        progress_callback=progress_callback
    )

    progress_bar.close()

    # Summary
    stats = processor.get_summary_stats()

    click.echo(f"\n{'='*60}")
    click.echo(f"  Processing Complete!")
    click.echo(f"{'='*60}")
    click.echo(f"  Total: {stats['total']}")
    click.echo(f"  Success: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    click.echo(f"  Failed: {stats['failed']}")
    click.echo(f"  Total Time: {stats['total_time_ms']/1000:.1f}s")
    click.echo(f"  Avg Time: {stats['avg_time_ms']:.0f}ms/image")

    if config['logging']['csv_enabled']:
        click.echo(f"\n  CSV Report: {csv_path}")

    click.echo(f"  Output Folder: {output_folder}")
    click.echo(f"{'='*60}\n")


if __name__ == '__main__':
    cli()
