from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING, Any, Tuple, Union, Dict, List

from .virtual_directory import VirtualDirectory
from .virtual_file import VirtualFile
from ...adapter.file import writefile, readfile
from ....file_manager.file_manager import FileManager

if TYPE_CHECKING:
    from common import WebRequest
    from server import Server
    from ....file_manager.file_manager import StrOrPath


class ExtendedFileManager(FileManager):
    _virtual_dirs: Dict[str, VirtualDirectory]

    @classmethod
    def override_grpc_method(cls, server: Server, name: str, callback) -> None:
        if type_and_api_def := server.moonraker_app.json_rpc.get_method(name):
            object.__setattr__(type_and_api_def[1], 'callback', callback)

    @classmethod
    def cast(cls, obj: FileManager) -> ExtendedFileManager:
        assert isinstance(obj, FileManager)
        obj.__class__ = cls
        assert isinstance(obj, ExtendedFileManager)
        setattr(obj, '_virtual_dirs', dict())
        cls.override_grpc_method(obj.server, 'server.files.get_roots', obj._handle_list_roots)
        return obj

    async def _handle_list_roots(self, web_request: WebRequest) -> List[Dict[str, Any]]:
        result = await super()._handle_list_roots(web_request)
        for name, paths in self._virtual_dirs.items():
            perms = "rw" if name in self.full_access_roots else "r"
            result.append({
                "name": name,
                "path": f'/virtual/{name}',  # TODO is it fine? should care?
                "permissions": perms
            })
        return result

    def _zip_files(self, item_list: List[str], destination: StrOrPath, store_only: bool = False) -> None:
        for item in item_list:
            root, str_path = self._convert_request_path(item)
            if root not in self.file_paths:
                raise self.server.error('Not supported for virtual directories')

        super()._zip_files(item_list, destination, store_only)

    def _parse_upload_args(self, upload_args: dict[str, Any]) -> dict[str, Any]:
        if (root := upload_args.get('root', '')) and (config := self._virtual_dirs.get(root, None)):
            if 'filename' not in upload_args:
                raise self.server.error("No file name specified in upload form")

            dir_path = upload_args.get('path', '').strip().lstrip('/')
            filename = upload_args.get('filename').strip().lstrip('/')
            request_file_path = os.path.join(dir_path, filename)

            dest_path = config.file_by_virtual_path(request_file_path).path
            if not dest_path:
                raise self.server.error('Cannot create files in virtual directories')

            return {
                'root': root,
                'filename': filename,
                'dir_path': dir_path,
                'dest_path': dest_path,
                'tmp_file_path': upload_args.get('tmp_file_path'),
                'start_print': False,
                'unzip_ufp': False,
                'ext': os.path.splitext(dest_path)[-1].lower(),
                'is_link': os.path.islink(dest_path),
                'user': upload_args.get('current_user')
            }

        return super()._parse_upload_args(upload_args)

    async def _process_uploaded_file(self, upload_info: Dict[str, Any]) -> Dict[str, Any]:
        if (root := upload_info.get('root')) and root in self._virtual_dirs:
            try:
                dest_path = upload_info['dest_path']
                if upload_info["is_link"]:
                    dest_path = os.path.realpath(dest_path)

                writefile(dest_path, readfile(upload_info['tmp_file_path']))

                return self.get_path_info(dest_path, root)
            except Exception:
                raise self.server.error("Unable to save file", 500)

        return await super()._process_uploaded_file(upload_info)

    def _convert_request_path(self, request_path: str) -> Tuple[str, str]:
        parts = os.path.normpath(request_path).strip("/").split("/", 1)
        if not parts:
            raise self.server.error(f"Invalid path: {request_path}")
        root = parts[0]
        if config := self._virtual_dirs.get(root, None):
            if len(parts) > 1:
                if file := config.file_by_virtual_path(parts[1]):
                    return config.name, file.path
            return config.name, f'/virtual/{config.name}'  # TODO is it fine? should care?
        return super()._convert_request_path(request_path)

    def _list_directory(self, path: str, root: str, is_extended: bool = False) -> Dict[str, Any]:
        if config := self._virtual_dirs.get(root, None):
            if not os.path.isdir(path):
                raise self.server.error(
                    f"Directory does not exist ({path})")
            self.check_reserved_path(path, False)
            flist: Dict[str, Any] = {'dirs': [], 'files': []}
            for file in config.files:
                full_path = file.path
                if not os.path.exists(full_path):
                    continue
                path_info = self.get_path_info(full_path, root)
                if os.path.isdir(full_path):
                    path_info['dirname'] = file.name
                    flist['dirs'].append(path_info)
                elif os.path.isfile(full_path):
                    path_info['filename'] = file.name
                    flist['files'].append(path_info)

            flist['disk_usage'] = shutil.disk_usage(path)._asdict()
            flist['root_info'] = {
                'name': root,
                'permissions': "rw" if root in self.full_access_roots else "r"
            }
            return flist
        return super()._list_directory(path, root, is_extended)

    def get_registered_dirs(self) -> List[str]:
        return list(self._virtual_dirs.keys()) + super().get_registered_dirs()

    def get_file_list(self, root: str, list_format: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if config := self._virtual_dirs.get(root, None):
            filelist: Dict[str, Any] = {}

            for file in config.files:
                if not os.path.exists(file.path):
                    continue
                filelist[file.name] = self.get_path_info(file.path, root)

            if list_format:
                flist: List[Dict[str, Any]] = []
                for name in sorted(filelist, key=str.lower):  # type: ignore
                    fdict: Dict[str, Any] = {'path': name}
                    fdict.update(filelist[name])
                    flist.append(fdict)
                return flist
            return filelist
        return super().get_file_list(root, list_format)

    def get_relative_path(self, root: str, full_path: str) -> str:
        if config := self._virtual_dirs.get(root, None):
            if file := config.file_by_local_path(full_path):
                return file.name
        return super().get_relative_path(root, full_path)

    def _check_file(self, name: str, path: str, full_access: bool):
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.islink(path):
            path = os.path.realpath(path)

        missing_perms = []
        if not os.access(path, os.R_OK, effective_ids=os.access in os.supports_effective_ids):
            missing_perms.append("READ")
        if full_access:
            if not os.access(path, os.W_OK, effective_ids=os.access in os.supports_effective_ids):
                missing_perms.append("WRITE")

        if missing_perms:
            mpstr = " | ".join(missing_perms)
            self.server.add_log_rollover_item(
                f"fm_reg_perms_{name}",
                f"file_manager: Moonraker has detected the following missing "
                f"permissions for root folder '{name}/{path}': {mpstr}"
            )

    def register_virtual_directory(self, name: str, files: list[str], full_access: bool = False) -> bool:
        if name in self.file_paths or not files:
            return False

        config = VirtualDirectory(name)
        for path in files:
            self._check_file(name, path, full_access)
            self.server.register_static_file_handler(f'{name}/{os.path.basename(path)}', path)
            config.files.append(VirtualFile.decode(path))

        if full_access:
            self.full_access_roots.add(name)

        self._virtual_dirs[name] = config

        if self.server.is_running():
            for path in files:
                self._sched_changed_event("root_update", name, path, immediate=True)

        return True
