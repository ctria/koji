
BEGIN;

-- debinfo tracks individual debs
-- buildroot_id can be NULL (for externally built packages)
-- we demand that N-V-R_A be unique we don't store filename
-- because filename should be N-V-R_A.deb
CREATE TABLE debinfo (
        id SERIAL NOT NULL PRIMARY KEY,
        build_id INTEGER REFERENCES build (id),
        buildroot_id INTEGER REFERENCES buildroot (id),
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        release TEXT NOT NULL,
        arch VARCHAR(16) NOT NULL,
        source TEXT NOT NULL,
        external_repo_id INTEGER NOT NULL REFERENCES external_repo(id),
        size BIGINT NOT NULL,
        metadata_only BOOLEAN NOT NULL DEFAULT FALSE,
        extra TEXT,
        CONSTRAINT debinfo_unique_nvra UNIQUE (name,version,release,arch,external_repo_id)
) WITHOUT OIDS;
CREATE INDEX debinfo_build ON debinfo(build_id);

COMMIT;
