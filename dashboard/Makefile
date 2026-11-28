.PHONY: build data wheel notebooks FORCE
build: data wheel notebooks

public := ../public/dashboard
build_config := Makefile ../pyproject.toml ../uv.lock
run := uv run --locked python
# コマンドラインの相対パスは、各ツールと同じくリポジトリのルート基準。
from_root = $(if $(filter /%,$(firstword $(1))),,../)$(1)
empty :=
space := $(empty) $(empty)
make_path = $(subst $(space),\$(space),$(1))
quote = '$(subst ','"'"',$(1))'

db := $(call from_root,$(or $(GAMEHARD_DB),/Users/hide/Documents/sqlite3/gamehard.db))
data_dir := $(call from_root,$(or $(PARQUET_OUTPUT),public/dashboard/data))
manifest := $(call make_path,$(data_dir)/manifest.json)
# 出力先ごとに入力 DB を記録。古い更新日時の別 DB に切り替えた場合も再生成する。
db_record := .build/data-$(shell python3 -c \
	'import hashlib, os, sys; print(hashlib.sha256(os.fsencode(os.path.realpath(sys.argv[1]))).hexdigest())' $(call quote,$(data_dir)))
data_ready := $(shell test -f $(db_record) && printf '%s\n' $(call quote,$(db)) | cmp -s - $(db_record) && \
	test ! $(call quote,$(data_dir)/manifest.json) -nt $(db_record) && \
	cd $(call quote,$(data_dir)) && test -f gamehard_info.parquet && \
	test -f gamehard_weekly.parquet && test -f gamehard_annotation.parquet && echo yes)
wal := $(call make_path,$(db)-wal)

data: $(manifest)
$(manifest): $(call make_path,$(db)) $(if $(wildcard $(wal)),$(wal)) \
		tools/export_parquet.py ../src/gamedata/data_source.py $(build_config) $(if $(data_ready),,FORCE)
	$(run) tools/export_parquet.py --db $(call quote,$(db)) --output $(call quote,$(data_dir))
	@mkdir -p .build
	@printf '%s\n' $(call quote,$(db)) > $(db_record)

packages := $(public)/packages
wheel_manifest := $(packages)/wheel.json
wheel_name := $(shell test ! -f $(wheel_manifest) || python3 -c \
	'import json, sys; print(json.load(open(sys.argv[1]))["filename"])' $(wheel_manifest))
wheel_sources := $(shell find ../src/gamedata -name __pycache__ -prune -o \
	\( -type d -o -type f ! -name '*.pyc' \) -print | sed 's/ /\\ /g')

wheel: $(wheel_manifest)
$(wheel_manifest): tools/build_wheel.py $(wheel_sources) ../README.md ../LICENSE $(build_config) \
		$(if $(and $(wheel_name),$(wildcard $(packages)/$(wheel_name))),,FORCE)
	$(run) tools/build_wheel.py

html_files := $(shell find notebooks -name __marimo__ -prune -o -type f -name '*.py' -print | \
	sed -e 's|^notebooks/|$(public)/|' -e 's/\.py$$/.html/' -e 's/ /\\ /g')
notebooks: $(html_files)
ifeq ($(strip $(html_files)),)
	$(error notebook が見つかりません: notebooks/)
endif

# 展開した notebook 名に空白がある場合も、前提ファイル1個として扱う。
.SECONDEXPANSION:
$(public)/%.html: $$(call make_path,notebooks/$$*.py) tools/export_notebooks.py $(build_config)
	$(run) tools/export_notebooks.py $(call quote,$<)
