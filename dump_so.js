rpc.exports = {
    findmodule: function(so_name) {
        var libso = Process.findModuleByName(so_name);
        return libso;
    },
    dumpmodule: function(so_name) {
        var libso = Process.findModuleByName(so_name);
        if (libso == null) {
            return -1;
        }
        Memory.protect(ptr(libso.base), libso.size, 'rwx');
        var CHUNK_SIZE = 50 * 1024 * 1024; // 50 MiB
        var numChunks = Math.ceil(libso.size / CHUNK_SIZE); // 计算总块数

        for (var i = 0; i < numChunks; i++) {
            var offset = i * CHUNK_SIZE;
            var size = Math.min(CHUNK_SIZE, libso.size - offset); // 确定每次实际传输的大小
            var chunk = ptr(libso.base).add(offset).readByteArray(size); // 读取块

            // 发送每块数据
            send({ chunk_index: i, total_chunks: numChunks }, chunk);
        }

        return { status: "complete", totalSize: libso.size };
    },

    allmodule: function() {
        return Process.enumerateModules()
    },
    arch: function() {
        return Process.arch;
    }
}
