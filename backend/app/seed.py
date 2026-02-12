"""Seed the database with realistic sample data for a small federal contractor.

Call via: flask seed
"""
from datetime import date, datetime, timezone
from app.extensions import db
from app.models.user import User
from app.models.people import Person
from app.models.location import Location
from app.models.security import SecurityBoundary
from app.models.asset import Asset, AssetRelationship
from app.models.license import License
from app.models.change import AssetChange

SESSION = '__default__'


def seed():
    """Seed the database with sample data."""
    db.create_all()

    # Clear existing default session data
    _clear_default_data()

    # Create demo user
    _create_users()

    # Create reference data
    people = _create_people()
    locations = _create_locations()
    boundaries = _create_security_boundaries()

    # Create assets
    hardware = _create_hardware_assets(people, locations, boundaries)
    software = _create_software_assets(people, locations, boundaries)
    cloud = _create_cloud_assets(people, locations, boundaries)
    contracts = _create_contract_assets(people, boundaries)

    all_assets = {**hardware, **software, **cloud, **contracts}

    # Create licenses
    licenses = _create_licenses(software)

    # Create relationships
    _create_relationships(all_assets, people, boundaries, licenses)

    # Create some change log entries
    _create_changes(all_assets)

    db.session.commit()


def _clear_default_data():
    """Clear existing seed data."""
    AssetChange.query.filter_by(session_id=SESSION).delete()
    AssetRelationship.query.filter_by(session_id=SESSION).delete()
    License.query.filter_by(session_id=SESSION).delete()
    Asset.query.filter_by(session_id=SESSION).delete()
    SecurityBoundary.query.filter_by(session_id=SESSION).delete()
    Location.query.filter_by(session_id=SESSION).delete()
    Person.query.filter_by(session_id=SESSION).delete()
    User.query.delete()
    db.session.commit()


def _create_users():
    """Create demo user accounts."""
    admin = User(username='admin', display_name='Admin User',
                 email='admin@assettracker.local', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    viewer = User(username='viewer', display_name='View Only User',
                  email='viewer@assettracker.local', role='viewer')
    viewer.set_password('viewer123')
    db.session.add(viewer)
    db.session.flush()


def _create_people():
    """Create 10 people for a small federal contractor."""
    people_data = [
        ('Sarah Chen', 'sarah.chen@novafederal.com', 'IT Director', 'IT Leadership', '703-555-0101'),
        ('Marcus Johnson', 'marcus.johnson@novafederal.com', 'Sr System Admin', 'Infrastructure', '703-555-0102'),
        ('Lisa Rodriguez', 'lisa.rodriguez@novafederal.com', 'Network Engineer', 'Infrastructure', '703-555-0103'),
        ('David Kim', 'david.kim@novafederal.com', 'Security Analyst', 'Cybersecurity', '703-555-0104'),
        ('Emily Watson', 'emily.watson@novafederal.com', 'Help Desk Lead', 'IT Support', '703-555-0105'),
        ('James Brown', 'james.brown@novafederal.com', 'Cloud Architect', 'Cloud Engineering', '703-555-0106'),
        ('Anna Petrov', 'anna.petrov@novafederal.com', 'DBA', 'Data Services', '703-555-0107'),
        ('Robert Williams', 'robert.williams@novafederal.com', 'DevOps Engineer', 'Engineering', '703-555-0108'),
        ('Maria Garcia', 'maria.garcia@novafederal.com', 'Compliance Officer', 'Compliance', '703-555-0109'),
        ('Tom Anderson', 'tom.anderson@novafederal.com', 'Procurement Manager', 'Procurement', '703-555-0110'),
    ]

    people = {}
    for name, email, role, team, phone in people_data:
        p = Person(name=name, email=email, role=role, team=team, phone=phone, session_id=SESSION)
        db.session.add(p)
        people[name] = p

    db.session.flush()
    return people


def _create_locations():
    """Create 5 locations."""
    locations_data = [
        ('Reston Main Office', 'office', '11955 Democracy Dr, Reston, VA 20190', 'Corporate headquarters, 3 floors'),
        ('AWS GovCloud US-East', 'cloud_region', 'us-gov-east-1', 'FedRAMP High authorized region'),
        ('Equinix DC', 'data_center', '21715 Filigree Ct, Ashburn, VA 20147', 'Colocation facility, 2 cabinets'),
        ('Azure Government', 'cloud_region', 'usgovvirginia', 'FedRAMP High authorized, Azure Gov'),
        ('Herndon Branch', 'office', '345 Elden St, Herndon, VA 20170', 'Satellite office, 15 seats'),
    ]

    locations = {}
    for name, loc_type, address, notes in locations_data:
        loc = Location(name=name, location_type=loc_type, address=address, notes=notes, session_id=SESSION)
        db.session.add(loc)
        locations[name] = loc

    db.session.flush()
    return locations


def _create_security_boundaries():
    """Create 2 security boundaries."""
    boundaries_data = [
        ('CUI Enclave', 'cui_boundary',
         'Controlled Unclassified Information boundary for all CUI-handling systems. '
         'Includes servers, workstations, and network segments that process, store, or transmit CUI.',
         'level_2', date(2025, 9, 15)),
        ('Corporate Network', 'corporate',
         'Standard corporate IT network for non-CUI business operations. '
         'Includes email, HR systems, and general business applications.',
         'level_1', date(2025, 6, 1)),
    ]

    boundaries = {}
    for name, b_type, desc, cmmc, assess_date in boundaries_data:
        b = SecurityBoundary(
            name=name, boundary_type=b_type, description=desc,
            cmmc_level=cmmc, assessment_date=assess_date, session_id=SESSION
        )
        db.session.add(b)
        boundaries[name] = b

    db.session.flush()
    return boundaries


def _create_hardware_assets(people, locations, boundaries):
    """Create ~15 hardware assets."""
    hw = {}

    # Production Servers
    hw['PROD-SVR-01'] = Asset(
        asset_type='hardware', sub_type='server', name='PROD-SVR-01',
        description='Dell PowerEdge R760 - Primary production server. Hosts Mission App and related services.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Dell Technologies', location_id=locations['Equinix DC'].id,
        attributes={'model': 'PowerEdge R760', 'cpu': '2x Intel Xeon Gold 6448Y', 'ram_gb': 512,
                    'storage': '8x 1.92TB NVMe SSD', 'serial': 'SVR-2024-0001'},
        acquired_date=date(2024, 3, 15), warranty_expiry=date(2027, 3, 15),
        last_audit_date=date(2025, 12, 1),
        tags=['production', 'cui', 'mission-critical'], session_id=SESSION,
    )

    hw['PROD-SVR-02'] = Asset(
        asset_type='hardware', sub_type='server', name='PROD-SVR-02',
        description='Dell PowerEdge R760 - Secondary production server. Hosts database and middleware.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Dell Technologies', location_id=locations['Equinix DC'].id,
        attributes={'model': 'PowerEdge R760', 'cpu': '2x Intel Xeon Gold 6448Y', 'ram_gb': 512,
                    'storage': '8x 3.84TB NVMe SSD', 'serial': 'SVR-2024-0002'},
        acquired_date=date(2024, 3, 15), warranty_expiry=date(2027, 3, 15),
        last_audit_date=date(2025, 12, 1),
        tags=['production', 'cui', 'database'], session_id=SESSION,
    )

    # Firewall
    hw['FW-CUI-01'] = Asset(
        asset_type='hardware', sub_type='firewall', name='FW-CUI-01',
        description='Cisco ASA 5525-X - Perimeter firewall for CUI Enclave. Manages all ingress/egress traffic.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Lisa Rodriguez'].id,
        managed_by_id=people['Lisa Rodriguez'].id,
        vendor='Cisco Systems', location_id=locations['Equinix DC'].id,
        attributes={'model': 'ASA 5525-X', 'firmware': '9.18.4', 'serial': 'FW-2023-0001'},
        acquired_date=date(2023, 6, 1), warranty_expiry=date(2026, 6, 1),
        last_audit_date=date(2025, 11, 15),
        tags=['firewall', 'cui', 'perimeter'], session_id=SESSION,
    )

    # Switches
    hw['SW-CORE-01'] = Asset(
        asset_type='hardware', sub_type='switch', name='SW-CORE-01',
        description='Cisco Catalyst 9300 - Core network switch for Equinix data center.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Lisa Rodriguez'].id,
        managed_by_id=people['Lisa Rodriguez'].id,
        vendor='Cisco Systems', location_id=locations['Equinix DC'].id,
        attributes={'model': 'Catalyst 9300-48P', 'ios_version': '17.9.4', 'serial': 'SW-2023-0001'},
        acquired_date=date(2023, 6, 1), warranty_expiry=date(2026, 6, 1),
        tags=['switch', 'core', 'data-center'], session_id=SESSION,
    )

    hw['SW-CORE-02'] = Asset(
        asset_type='hardware', sub_type='switch', name='SW-CORE-02',
        description='Cisco Catalyst 9300 - Core network switch for Reston office.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Lisa Rodriguez'].id,
        managed_by_id=people['Lisa Rodriguez'].id,
        vendor='Cisco Systems', location_id=locations['Reston Main Office'].id,
        attributes={'model': 'Catalyst 9300-24P', 'ios_version': '17.9.4', 'serial': 'SW-2023-0002'},
        acquired_date=date(2023, 8, 15), warranty_expiry=date(2026, 8, 15),
        tags=['switch', 'core', 'office'], session_id=SESSION,
    )

    # Laptops (8 assigned to staff)
    laptop_assignments = [
        ('LT-001', 'Sarah Chen'),
        ('LT-002', 'Marcus Johnson'),
        ('LT-003', 'Lisa Rodriguez'),
        ('LT-004', 'David Kim'),
        ('LT-005', 'Emily Watson'),
        ('LT-006', 'James Brown'),
        ('LT-007', 'Anna Petrov'),
        ('LT-008', 'Robert Williams'),
    ]
    for lt_name, person_name in laptop_assignments:
        hw[lt_name] = Asset(
            asset_type='hardware', sub_type='laptop', name=lt_name,
            description=f'Dell Latitude 5540 - Assigned to {person_name}. '
                        f'Standard-issue laptop with CUI-capable encryption.',
            status='active', data_classification='CUI',
            security_boundary_id=boundaries['CUI Enclave'].id,
            owner_id=people[person_name].id,
            managed_by_id=people['Emily Watson'].id,
            vendor='Dell Technologies', location_id=locations['Reston Main Office'].id,
            attributes={'model': 'Latitude 5540', 'cpu': 'Intel Core i7-1365U', 'ram_gb': 32,
                        'storage': '512GB NVMe SSD', 'serial': f'LT-2024-{lt_name[-3:]}',
                        'bitlocker': True, 'tpm_version': '2.0'},
            acquired_date=date(2024, 1, 10), warranty_expiry=date(2027, 1, 10),
            last_audit_date=date(2025, 11, 1),
            tags=['laptop', 'endpoint', 'cui'], session_id=SESSION,
        )

    # NAS
    hw['NAS-BKP-01'] = Asset(
        asset_type='hardware', sub_type='nas', name='NAS-BKP-01',
        description='Synology RS1221+ - Network attached storage for local backups.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Marcus Johnson'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Synology', location_id=locations['Equinix DC'].id,
        attributes={'model': 'RS1221+', 'capacity_tb': 48, 'raid': 'RAID 6', 'serial': 'NAS-2024-0001'},
        acquired_date=date(2024, 5, 1), warranty_expiry=date(2027, 5, 1),
        tags=['backup', 'storage', 'cui'], session_id=SESSION,
    )

    # Printer
    hw['PRN-RST-01'] = Asset(
        asset_type='hardware', sub_type='printer', name='PRN-RST-01',
        description='HP LaserJet Enterprise M610 - Shared office printer in Reston.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Emily Watson'].id,
        managed_by_id=people['Emily Watson'].id,
        vendor='HP Inc.', location_id=locations['Reston Main Office'].id,
        attributes={'model': 'LaserJet Enterprise M610', 'serial': 'PRN-2024-0001'},
        acquired_date=date(2024, 2, 1), warranty_expiry=date(2027, 2, 1),
        tags=['printer', 'office'], session_id=SESSION,
    )

    for asset in hw.values():
        db.session.add(asset)
    db.session.flush()
    return hw


def _create_software_assets(people, locations, boundaries):
    """Create ~12 software assets."""
    sw = {}

    sw['Windows Server 2022'] = Asset(
        asset_type='software', sub_type='operating_system', name='Windows Server 2022',
        description='Microsoft Windows Server 2022 Datacenter - On PROD-SVR-01.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Microsoft',
        attributes={'version': '2022 Datacenter', 'edition': 'Datacenter', 'patch_level': '21H2'},
        tags=['os', 'windows', 'server'], session_id=SESSION,
    )

    sw['RHEL 9'] = Asset(
        asset_type='software', sub_type='operating_system', name='RHEL 9',
        description='Red Hat Enterprise Linux 9 - On PROD-SVR-02 for database workloads.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Red Hat',
        attributes={'version': '9.3', 'kernel': '5.14.0-362.el9'},
        tags=['os', 'linux', 'server'], session_id=SESSION,
    )

    sw['Microsoft 365 GCC'] = Asset(
        asset_type='software', sub_type='SaaS', name='Microsoft 365 GCC',
        description='Microsoft 365 Government Community Cloud - Email, Teams, SharePoint, OneDrive.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Microsoft',
        attributes={'plan': 'GCC High', 'tenant_id': 'novafed-gcc'},
        tags=['saas', 'email', 'collaboration'], session_id=SESSION,
    )

    sw['CrowdStrike Falcon'] = Asset(
        asset_type='software', sub_type='security', name='CrowdStrike Falcon',
        description='CrowdStrike Falcon - Endpoint detection and response (EDR) platform.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['David Kim'].id,
        vendor='CrowdStrike',
        attributes={'module': 'Falcon Prevent + Insight', 'fedramp': 'Moderate'},
        tags=['security', 'edr', 'endpoint'], session_id=SESSION,
    )

    sw['Nessus Professional'] = Asset(
        asset_type='software', sub_type='security', name='Nessus Professional',
        description='Tenable Nessus Professional - Vulnerability scanner for periodic assessments.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['David Kim'].id,
        vendor='Tenable',
        attributes={'version': '10.6'},
        tags=['security', 'vulnerability-scanner'], session_id=SESSION,
    )

    sw['Splunk Enterprise'] = Asset(
        asset_type='software', sub_type='security', name='Splunk Enterprise',
        description='Splunk Enterprise - SIEM and log aggregation for security monitoring.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['David Kim'].id,
        vendor='Splunk',
        attributes={'version': '9.2', 'daily_ingest_gb': 5},
        tags=['security', 'siem', 'logging'], session_id=SESSION,
    )

    sw['Mission App v3.2'] = Asset(
        asset_type='software', sub_type='custom_app', name='Mission App v3.2',
        description='Custom Java/Spring Boot application - Core mission delivery platform for DHS contract.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Robert Williams'].id,
        vendor=None,
        attributes={'framework': 'Spring Boot 3.2', 'language': 'Java 17', 'kind': 'IN_HOUSE'},
        tags=['custom', 'mission-critical', 'java'], session_id=SESSION,
    )

    sw['PostgreSQL 15'] = Asset(
        asset_type='software', sub_type='database', name='PostgreSQL 15',
        description='PostgreSQL 15 - Primary relational database for Mission App.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Anna Petrov'].id,
        managed_by_id=people['Anna Petrov'].id,
        vendor='PostgreSQL',
        attributes={'version': '15.5', 'extensions': ['pgcrypto', 'pg_stat_statements']},
        tags=['database', 'postgresql', 'mission-critical'], session_id=SESSION,
    )

    sw['Apache Tomcat 10'] = Asset(
        asset_type='software', sub_type='middleware', name='Apache Tomcat 10',
        description='Apache Tomcat 10 - Application server hosting Mission App.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        managed_by_id=people['Robert Williams'].id,
        vendor='Apache Software Foundation',
        attributes={'version': '10.1.18'},
        tags=['middleware', 'app-server'], session_id=SESSION,
    )

    sw['GitLab'] = Asset(
        asset_type='software', sub_type='devtools', name='GitLab',
        description='GitLab Premium - Source control, CI/CD, and project management.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Robert Williams'].id,
        managed_by_id=people['Robert Williams'].id,
        vendor='GitLab Inc.',
        attributes={'plan': 'Premium', 'deployment': 'SaaS'},
        tags=['devtools', 'source-control', 'ci-cd'], session_id=SESSION,
    )

    sw['Jira/Confluence'] = Asset(
        asset_type='software', sub_type='SaaS', name='Jira/Confluence',
        description='Atlassian Jira + Confluence Cloud - Project management and documentation.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Robert Williams'].id,
        vendor='Atlassian',
        attributes={'plan': 'Premium', 'products': ['Jira Software', 'Confluence']},
        tags=['project-management', 'documentation', 'saas'], session_id=SESSION,
    )

    sw['ServiceNow Express'] = Asset(
        asset_type='software', sub_type='SaaS', name='ServiceNow Express',
        description='ServiceNow Express - IT Service Management (ITSM) platform.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Emily Watson'].id,
        managed_by_id=people['Emily Watson'].id,
        vendor='ServiceNow',
        attributes={'edition': 'Express', 'modules': ['Incident', 'Change', 'Asset']},
        tags=['itsm', 'service-desk', 'saas'], session_id=SESSION,
    )

    for asset in sw.values():
        db.session.add(asset)
    db.session.flush()
    return sw


def _create_cloud_assets(people, locations, boundaries):
    """Create ~8 cloud service assets."""
    cloud = {}

    cloud['AWS EC2 - Mission App'] = Asset(
        asset_type='cloud_service', sub_type='IaaS', name='AWS EC2 - Mission App',
        description='AWS GovCloud EC2 instance hosting Mission App production environment.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['James Brown'].id,
        managed_by_id=people['James Brown'].id,
        vendor='Amazon Web Services',
        location_id=locations['AWS GovCloud US-East'].id,
        attributes={'instance_type': 'm6i.2xlarge', 'ami': 'RHEL 9', 'account': 'novafed-govcloud'},
        tags=['aws', 'ec2', 'production'], session_id=SESSION,
    )

    cloud['AWS EC2 - Staging'] = Asset(
        asset_type='cloud_service', sub_type='IaaS', name='AWS EC2 - Staging',
        description='AWS GovCloud EC2 instance for staging/test environment.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['James Brown'].id,
        managed_by_id=people['Robert Williams'].id,
        vendor='Amazon Web Services',
        location_id=locations['AWS GovCloud US-East'].id,
        attributes={'instance_type': 'm6i.xlarge', 'ami': 'RHEL 9', 'account': 'novafed-govcloud'},
        tags=['aws', 'ec2', 'staging'], session_id=SESSION,
    )

    cloud['AWS RDS PostgreSQL'] = Asset(
        asset_type='cloud_service', sub_type='PaaS', name='AWS RDS PostgreSQL',
        description='AWS GovCloud RDS PostgreSQL - Managed database for Mission App cloud deployment.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Anna Petrov'].id,
        managed_by_id=people['Anna Petrov'].id,
        vendor='Amazon Web Services',
        location_id=locations['AWS GovCloud US-East'].id,
        attributes={'engine': 'PostgreSQL 15.5', 'instance_class': 'db.r6g.xlarge',
                    'storage_gb': 500, 'multi_az': True},
        tags=['aws', 'rds', 'database', 'production'], session_id=SESSION,
    )

    cloud['AWS S3 - Documents'] = Asset(
        asset_type='cloud_service', sub_type='storage', name='AWS S3 - Documents',
        description='AWS GovCloud S3 bucket for CUI document storage. SSE-KMS encrypted.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['James Brown'].id,
        managed_by_id=people['James Brown'].id,
        vendor='Amazon Web Services',
        location_id=locations['AWS GovCloud US-East'].id,
        attributes={'bucket': 'novafed-cui-documents', 'encryption': 'SSE-KMS',
                    'versioning': True, 'lifecycle': '90-day-glacier'},
        tags=['aws', 's3', 'storage', 'cui'], session_id=SESSION,
    )

    cloud['AWS CloudTrail'] = Asset(
        asset_type='cloud_service', sub_type='monitoring', name='AWS CloudTrail',
        description='AWS CloudTrail - API audit logging for all GovCloud activity.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['James Brown'].id,
        vendor='Amazon Web Services',
        location_id=locations['AWS GovCloud US-East'].id,
        attributes={'trail_type': 'organization', 'log_destination': 's3'},
        tags=['aws', 'audit', 'logging', 'compliance'], session_id=SESSION,
    )

    cloud['Azure AD / Entra ID'] = Asset(
        asset_type='cloud_service', sub_type='identity', name='Azure AD / Entra ID',
        description='Microsoft Entra ID (Azure AD) - Identity and access management for all cloud services.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['Marcus Johnson'].id,
        vendor='Microsoft',
        location_id=locations['Azure Government'].id,
        attributes={'tenant': 'novafed-gov', 'mfa': 'enforced', 'conditional_access': True},
        tags=['identity', 'azure', 'sso', 'mfa'], session_id=SESSION,
    )

    cloud['Zoom for Government'] = Asset(
        asset_type='cloud_service', sub_type='SaaS', name='Zoom for Government',
        description='Zoom for Government - FedRAMP Moderate video conferencing.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Emily Watson'].id,
        vendor='Zoom Video Communications',
        attributes={'plan': 'Government', 'fedramp': 'Moderate'},
        tags=['collaboration', 'video', 'saas'], session_id=SESSION,
    )

    cloud['Slack Enterprise Grid'] = Asset(
        asset_type='cloud_service', sub_type='SaaS', name='Slack Enterprise Grid',
        description='Slack Enterprise Grid - Team messaging with DLP and eDiscovery.',
        status='active', data_classification='internal',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Sarah Chen'].id,
        managed_by_id=people['Emily Watson'].id,
        vendor='Salesforce (Slack)',
        attributes={'plan': 'Enterprise Grid', 'fedramp': 'Moderate'},
        tags=['collaboration', 'messaging', 'saas'], session_id=SESSION,
    )

    cloud['Zscaler'] = Asset(
        asset_type='cloud_service', sub_type='security', name='Zscaler',
        description='Zscaler Internet Access (ZIA) - Cloud-based web security gateway.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['David Kim'].id,
        managed_by_id=people['Lisa Rodriguez'].id,
        vendor='Zscaler',
        attributes={'product': 'ZIA', 'fedramp': 'High'},
        tags=['security', 'web-proxy', 'zero-trust'], session_id=SESSION,
    )

    for asset in cloud.values():
        db.session.add(asset)
    db.session.flush()
    return cloud


def _create_contract_assets(people, boundaries):
    """Create 3 contract assets."""
    contracts = {}

    contracts['DHS Cybersecurity Support'] = Asset(
        asset_type='contract', sub_type='federal_contract', name='DHS Cybersecurity Support',
        description='DHS Cybersecurity Operations Support contract. Provides cyber analysts and '
                    'incident response capabilities. CMMC Level 2 required.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        vendor='Department of Homeland Security',
        attributes={'contract_number': 'HSHQDC-25-C-00123', 'period_of_performance': '2025-2027',
                    'value': 4500000, 'cmmc_required': 'Level 2', 'naics': '541512'},
        acquired_date=date(2025, 1, 15),
        tags=['federal', 'dhs', 'cybersecurity', 'cui'], session_id=SESSION,
    )

    contracts['DoD IT Modernization'] = Asset(
        asset_type='contract', sub_type='federal_contract', name='DoD IT Modernization',
        description='DoD IT Modernization Task Order under SEWP V. Cloud migration and '
                    'application modernization services.',
        status='active', data_classification='CUI',
        security_boundary_id=boundaries['CUI Enclave'].id,
        owner_id=people['Sarah Chen'].id,
        vendor='Department of Defense',
        attributes={'contract_number': 'NNG15SD89B-TO-0042', 'vehicle': 'SEWP V',
                    'period_of_performance': '2025-2028', 'value': 8200000,
                    'cmmc_required': 'Level 2', 'naics': '541519'},
        acquired_date=date(2025, 4, 1),
        tags=['federal', 'dod', 'modernization', 'cui'], session_id=SESSION,
    )

    contracts['VA Helpdesk Support'] = Asset(
        asset_type='contract', sub_type='federal_contract', name='VA Helpdesk Support',
        description='VA IT Helpdesk Support Services. Tier 1/2 support for VA regional offices.',
        status='active', data_classification='FCI',
        security_boundary_id=boundaries['Corporate Network'].id,
        owner_id=people['Emily Watson'].id,
        vendor='Department of Veterans Affairs',
        attributes={'contract_number': 'VA-ITC-25-P-0078', 'period_of_performance': '2025-2026',
                    'value': 1200000, 'cmmc_required': 'Level 1', 'naics': '541513'},
        acquired_date=date(2025, 2, 1),
        tags=['federal', 'va', 'helpdesk', 'fci'], session_id=SESSION,
    )

    for asset in contracts.values():
        db.session.add(asset)
    db.session.flush()
    return contracts


def _create_licenses(software):
    """Create 8 licenses linked to software assets."""
    licenses = {}

    licenses['M365 GCC License'] = License(
        software_asset_id=software['Microsoft 365 GCC'].id,
        license_type='per_seat', vendor='Microsoft',
        total_seats=15, used_seats=12, cost_per_period=22.0, billing_period='monthly',
        start_date=date(2025, 1, 1), expiry_date=date(2026, 12, 31),
        auto_renew=True, contract_number='MS-GOV-2025-001',
        notes='GCC High plan for CUI handling',
        session_id=SESSION,
    )

    licenses['CrowdStrike License'] = License(
        software_asset_id=software['CrowdStrike Falcon'].id,
        license_type='per_seat', vendor='CrowdStrike',
        total_seats=20, used_seats=18, cost_per_period=15.0, billing_period='monthly',
        start_date=date(2025, 3, 15), expiry_date=date(2026, 3, 15),
        auto_renew=False, contract_number='CS-FED-2025-042',
        notes='Falcon Prevent + Insight. Renewal pending budget approval.',
        session_id=SESSION,
    )

    licenses['Nessus License'] = License(
        software_asset_id=software['Nessus Professional'].id,
        license_type='subscription', vendor='Tenable',
        total_seats=1, used_seats=1, cost_per_period=3500.0, billing_period='annual',
        start_date=date(2025, 5, 1), expiry_date=date(2026, 4, 30),
        auto_renew=True, contract_number='TEN-2025-0088',
        notes='Single professional license for vulnerability assessments',
        session_id=SESSION,
    )

    licenses['Splunk License'] = License(
        software_asset_id=software['Splunk Enterprise'].id,
        license_type='subscription', vendor='Splunk',
        total_seats=None, used_seats=None, cost_per_period=1800.0, billing_period='monthly',
        start_date=date(2025, 1, 1), expiry_date=date(2026, 8, 31),
        auto_renew=True, contract_number='SPL-ENT-2025-015',
        notes='5GB/day ingest license',
        session_id=SESSION,
    )

    licenses['Jira License'] = License(
        software_asset_id=software['Jira/Confluence'].id,
        license_type='per_seat', vendor='Atlassian',
        total_seats=25, used_seats=20, cost_per_period=10.0, billing_period='monthly',
        start_date=date(2025, 1, 15), expiry_date=date(2027, 1, 15),
        auto_renew=True, contract_number='ATL-2025-0033',
        notes='Jira Software + Confluence Premium bundle',
        session_id=SESSION,
    )

    licenses['GitLab License'] = License(
        software_asset_id=software['GitLab'].id,
        license_type='per_seat', vendor='GitLab Inc.',
        total_seats=15, used_seats=12, cost_per_period=19.0, billing_period='monthly',
        start_date=date(2025, 7, 1), expiry_date=date(2026, 6, 30),
        auto_renew=True, contract_number='GL-PREM-2025-007',
        notes='GitLab Premium SaaS',
        session_id=SESSION,
    )

    licenses['Zoom License'] = License(
        software_asset_id=None,  # Will link to cloud asset separately
        license_type='per_seat', vendor='Zoom Video Communications',
        total_seats=20, used_seats=15, cost_per_period=16.0, billing_period='monthly',
        start_date=date(2025, 1, 1), expiry_date=date(2026, 9, 30),
        auto_renew=True, contract_number='ZM-GOV-2025-012',
        notes='Zoom for Government plan',
        session_id=SESSION,
    )

    licenses['ServiceNow License'] = License(
        software_asset_id=software['ServiceNow Express'].id,
        license_type='per_seat', vendor='ServiceNow',
        total_seats=10, used_seats=8, cost_per_period=100.0, billing_period='monthly',
        start_date=date(2025, 6, 1), expiry_date=date(2026, 5, 31),
        auto_renew=False, contract_number='SN-EXP-2025-019',
        notes='Express edition, 10 agent seats',
        session_id=SESSION,
    )

    for lic in licenses.values():
        db.session.add(lic)
    db.session.flush()
    return licenses


def _create_relationships(assets, people, boundaries, licenses):
    """Create 30+ relationships between assets."""
    rels = []

    def rel(source_name, target_name, rel_type, desc=None):
        s = assets.get(source_name)
        t = assets.get(target_name)
        if s and t:
            r = AssetRelationship(
                source_asset_id=s.id, target_asset_id=t.id,
                relationship_type=rel_type, description=desc, session_id=SESSION,
            )
            rels.append(r)

    # Servers run software
    rel('PROD-SVR-01', 'Mission App v3.2', 'runs', 'Production server hosts Mission App')
    rel('PROD-SVR-01', 'Apache Tomcat 10', 'runs', 'Tomcat application server on PROD-SVR-01')
    rel('PROD-SVR-01', 'Windows Server 2022', 'runs', 'OS on PROD-SVR-01')
    rel('PROD-SVR-02', 'PostgreSQL 15', 'runs', 'Database server on PROD-SVR-02')
    rel('PROD-SVR-02', 'RHEL 9', 'runs', 'RHEL 9 operating system on PROD-SVR-02')

    # Application dependencies
    rel('Mission App v3.2', 'PostgreSQL 15', 'depends_on', 'Mission App primary database')
    rel('Mission App v3.2', 'AWS S3 - Documents', 'depends_on', 'Document storage for Mission App')
    rel('Mission App v3.2', 'Apache Tomcat 10', 'depends_on', 'Runs on Tomcat app server')
    rel('Mission App v3.2', 'Azure AD / Entra ID', 'depends_on', 'SSO/authentication provider')

    # Contract support
    rel('Mission App v3.2', 'DHS Cybersecurity Support', 'supports', 'Core deliverable for DHS contract')
    rel('AWS EC2 - Mission App', 'DoD IT Modernization', 'supports', 'Cloud hosting for DoD modernization')
    rel('ServiceNow Express', 'VA Helpdesk Support', 'supports', 'ITSM platform for VA helpdesk')

    # Firewall protects
    rel('FW-CUI-01', 'PROD-SVR-01', 'protects', 'Perimeter firewall for CUI servers')
    rel('FW-CUI-01', 'PROD-SVR-02', 'protects', 'Perimeter firewall for CUI servers')

    # CrowdStrike installed on endpoints
    for endpoint in ['PROD-SVR-01', 'PROD-SVR-02', 'LT-001', 'LT-002', 'LT-003',
                     'LT-004', 'LT-005', 'LT-006', 'LT-007', 'LT-008']:
        rel('CrowdStrike Falcon', endpoint, 'installed_on', f'EDR agent on {endpoint}')

    # Splunk collects from
    rel('Splunk Enterprise', 'FW-CUI-01', 'depends_on', 'Collects firewall logs')
    rel('Splunk Enterprise', 'AWS CloudTrail', 'depends_on', 'Ingests CloudTrail audit logs')

    # Cloud service dependencies
    rel('AWS EC2 - Mission App', 'Mission App v3.2', 'runs', 'Cloud instance runs Mission App')
    rel('AWS RDS PostgreSQL', 'PostgreSQL 15', 'runs', 'Managed RDS runs PostgreSQL')
    rel('AWS EC2 - Staging', 'Mission App v3.2', 'runs', 'Staging instance for Mission App')

    # Zscaler web security
    rel('Zscaler', 'FW-CUI-01', 'supports', 'Cloud web security complements firewall')

    # Nessus scans
    rel('Nessus Professional', 'PROD-SVR-01', 'supports', 'Vulnerability scanning')
    rel('Nessus Professional', 'PROD-SVR-02', 'supports', 'Vulnerability scanning')

    # NAS backup
    rel('NAS-BKP-01', 'PROD-SVR-01', 'supports', 'Local backup for server data')
    rel('NAS-BKP-01', 'PROD-SVR-02', 'supports', 'Local backup for server data')

    # GitLab supports development
    rel('GitLab', 'Mission App v3.2', 'supports', 'Source control and CI/CD for Mission App')

    # Jira supports project management
    rel('Jira/Confluence', 'DHS Cybersecurity Support', 'supports', 'Project tracking for DHS contract')
    rel('Jira/Confluence', 'DoD IT Modernization', 'supports', 'Project tracking for DoD contract')

    for r in rels:
        db.session.add(r)
    db.session.flush()


def _create_changes(assets):
    """Create some sample change log entries."""
    now = datetime.now(timezone.utc)
    changes = [
        AssetChange(
            asset_id=assets['Mission App v3.2'].id,
            changed_by='robert.williams@novafederal.com',
            change_type='updated',
            field_changed='attributes',
            old_value='version: 3.1',
            new_value='version: 3.2',
            changed_at=now,
            notes='Deployed v3.2 with CMMC compliance updates',
            session_id=SESSION,
        ),
        AssetChange(
            asset_id=assets['PROD-SVR-01'].id,
            changed_by='marcus.johnson@novafederal.com',
            change_type='updated',
            field_changed='last_audit_date',
            old_value='2025-09-01',
            new_value='2025-12-01',
            changed_at=now,
            notes='Quarterly security audit completed',
            session_id=SESSION,
        ),
        AssetChange(
            asset_id=assets['CrowdStrike Falcon'].id,
            changed_by='david.kim@novafederal.com',
            change_type='updated',
            field_changed='attributes',
            old_value='sensor: 7.10',
            new_value='sensor: 7.12',
            changed_at=now,
            notes='Updated Falcon sensor to latest version across all endpoints',
            session_id=SESSION,
        ),
        AssetChange(
            asset_id=assets['AWS EC2 - Staging'].id,
            changed_by='james.brown@novafederal.com',
            change_type='created',
            changed_at=now,
            notes='Provisioned new staging EC2 instance for DoD modernization testing',
            session_id=SESSION,
        ),
        AssetChange(
            asset_id=assets['FW-CUI-01'].id,
            changed_by='lisa.rodriguez@novafederal.com',
            change_type='updated',
            field_changed='attributes',
            old_value='firmware: 9.18.3',
            new_value='firmware: 9.18.4',
            changed_at=now,
            notes='Critical firmware update applied per CISA advisory',
            session_id=SESSION,
        ),
    ]

    for c in changes:
        db.session.add(c)
    db.session.flush()
