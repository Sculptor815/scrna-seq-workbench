"""Visible runtime notice and explicit backend/device selection, without fallbacks."""
import sys

PIPELINE_NOTICE = (
    'The complete pipeline may take more than 1 hour, depending on data size, '
    'hardware, training and review steps. scVI is the default. With a compatible '
    'CUDA GPU, use GPU scVI. Without one, you can wait for CPU scVI or explicitly '
    'choose Harmony (harmonypy) for verified technical batches. Harmony often '
    'takes less time but has different assumptions and does not guarantee a '
    'completion time or equivalent biological results. No automatic backend switch.'
)


def announce_runtime(args, report):
    print(PIPELINE_NOTICE, file=sys.stderr, flush=True)
    report['runtime_choice'] = {
        'notice': PIPELINE_NOTICE, 'default_backend': 'scvi',
        'selected_backend': args.backend, 'requested_device': args.device,
        'decision_reason': getattr(args, 'backend_reason', None),
        'automatic_backend_fallback': False,
    }


def resolve_device(args, report):
    if args.backend == 'harmony':
        if args.device == 'gpu':
            raise ValueError('Harmony uses CPU; select --device cpu or auto')
        device = 'cpu'
    else:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError('Install requirements-scvi.txt for the selected scVI backend; no automatic Harmony fallback.') from exc
        available = bool(torch.cuda.is_available())
        report['runtime_choice']['cuda_available'] = available
        device = ('gpu' if available else 'cpu') if args.device == 'auto' else args.device
        if device == 'gpu' and not available:
            raise ValueError('Requested CUDA GPU is unavailable. Choose CPU scVI or explicitly select Harmony with verified batches.')
        if device == 'cpu':
            message = 'Running CPU scVI; training can take substantially longer. The backend remains scVI.'
            report['warnings'].append(message)
            print(message, file=sys.stderr, flush=True)
    report['runtime_choice']['actual_device'] = device
    return device
