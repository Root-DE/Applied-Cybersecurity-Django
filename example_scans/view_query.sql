-- Query for the vulnerability view
DROP MATERIALIZED VIEW IF EXISTS vulnerabilities CASCADE;
CREATE MATERIALIZED VIEW vulnerabilities AS
WITH 
    vulns AS (  -- get the single vulnerability objects!
        SELECT id, created_at, repository_id, jsonb_array_elements(grype_scan->'matches') AS vuln
        FROM vuln_backend_artifactdata
    ), 
    cvss_data AS (  -- get the cvss data for each vulnerability (preferred namespace 'nvd')
        SELECT id, created_at, repository_id, cvss_data->>'id' AS vuln_id, cvss_data->>'severity' AS severity, cvss_data->'cvss' AS cvss, vuln
        FROM (
            SELECT id, created_at, repository_id, vuln, 
                CASE 
                    WHEN vuln->'vulnerability' @> '{"namespace":"nvd"}'::jsonb THEN vuln->'vulnerability'   -- nvd at first level
                    ELSE (                                                                                  -- nvd at another level? Otherwise top level data
                        SELECT rvuln
                        FROM jsonb_array_elements(vuln->'relatedVulnerabilities') AS rvuln
                        WHERE rvuln->>'namespace' = 'nvd'
                        UNION ALL
                        SELECT vuln->'vulnerability'
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM jsonb_array_elements(vuln->'relatedVulnerabilities') AS rvuln
                            WHERE rvuln->>'namespace' = 'nvd'
                        )
                        LIMIT 1
                    )
                END AS cvss_data 
            FROM vulns
        ) as cvss_data
    ), 
    remaining_data AS (  -- get the artifact and the fix data for each vulnerability
        SELECT id, created_at, repository_id, vuln_id, severity, cvss, vuln->'artifact'->>'name' as artifact_name, vuln->'artifact'->>'version' as artifact_version, vuln->'artifact'->>'purl' as artifact_purl, vuln->'artifact'->'cpes' as artifact_cpes, vuln->'vulnerability'->'fix' as fix
        FROM cvss_data
    )

SELECT *
FROM remaining_data;

CREATE OR REPLACE FUNCTION tri_artifact_data_func() RETURNS TRIGGER AS $$ BEGIN REFRESH MATERIALIZED VIEW vulnerabilities; RETURN NULL; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER tri_artifact_data AFTER INSERT OR UPDATE OR DELETE ON vuln_backend_artifactdata FOR EACH STATEMENT EXECUTE PROCEDURE tri_artifact_data_func();
