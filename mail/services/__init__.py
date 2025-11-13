"""
Email and Domain Management Services
"""
from .domain_manager import DomainManager, NamecheapDomainService

# Import DjangoEmailService from services.py (parent module)
import importlib.util
import os
parent_dir = os.path.dirname(os.path.dirname(__file__))
services_file = os.path.join(parent_dir, 'services.py')
if os.path.exists(services_file):
    spec = importlib.util.spec_from_file_location("mail.services_module", services_file)
    services_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(services_module)
    DjangoEmailService = services_module.DjangoEmailService
else:
    DjangoEmailService = None

__all__ = ['DomainManager', 'NamecheapDomainService']
if DjangoEmailService:
    __all__.append('DjangoEmailService')

