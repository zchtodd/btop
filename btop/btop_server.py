import json

import asyncio
import websockets
import psutil


class BtopServer(object):
    def __init__(self, port):
        self.websockets = []
        self.port = port

        self.prev_procs = {}
        self.curr_procs = {}

        self.cpu = {}
        self.mem = {"total": 0, "used": 0, "percent": 0}
        self.swp = {"total": 0, "used": 0, "percent": 0}
        self.processes = []

    def start(self):
        ws_server = websockets.serve(self.handle_conn, "0.0.0.0", self.port)

        asyncio.ensure_future(self.update())

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(ws_server)
        self.loop.run_forever()

    async def handle_conn(self, websocket, path):
        await websocket.send(
            json.dumps(
                {
                    "cpu": self.cpu,
                    "mem": self.mem,
                    "swp": self.swp,
                    "add": self.processes,
                    "update": [],
                    "remove": [],
                }
            )
        )

        self.websockets.append(websocket)

        try:
            async for message in websocket:  # noqa
                pass
        finally:
            if websocket in self.websockets:
                self.websockets.remove(websocket)

    async def broadcast(self, payload):
        i = len(self.websockets) - 1
        while i >= 0:
            try:
                await self.websockets[i].send(payload)
            except websockets.exceptions.ConnectionClosed:
                self.websockets.pop(i)
            i -= 1

    async def update(self):
        self.cpu = psutil.cpu_percent(percpu=True)
        self.processes = [
            p.as_dict(
                attrs=(
                    "pid",
                    "username",
                    "nice",
                    "memory_info",
                    "status",
                    "cpu_percent",
                    "memory_percent",
                    "cmdline",
                )
            )
            for p in psutil.process_iter()
        ]

        for process in self.processes:
            process["cpu_percent"] = round(process["cpu_percent"], 2)
            process["memory_percent"] = round(process["memory_percent"], 2)
            process["cmdline"] = " ".join(process["cmdline"])

        swp = psutil.swap_memory()
        self.swp = {"total": swp.total, "used": swp.used, "perc": swp.percent}

        mem = psutil.virtual_memory()
        self.mem = {"total": mem.total, "used": mem.used, "perc": mem.percent}

        self.prev_procs = self.curr_procs
        self.curr_procs = {p["pid"]: p for p in self.processes}

        added = [
            self.curr_procs[pid]
            for pid in self.curr_procs
            if pid not in self.prev_procs
        ]

        removed = [
            self.prev_procs[pid]
            for pid in self.prev_procs
            if pid not in self.curr_procs
        ]

        updated = []
        for pid, proc in self.curr_procs.items():
            if pid in self.prev_procs:
                pproc = self.prev_procs[pid]
                for attr in ("cpu_percent", "memory_percent"):
                    if proc[attr] != pproc[attr]:
                        updated.append(proc)
                        break

        await self.broadcast(
            json.dumps(
                {
                    "cpu": self.cpu,
                    "mem": self.mem,
                    "swp": self.swp,
                    "add": added,
                    "update": updated,
                    "remove": removed,
                }
            )
        )
        await asyncio.sleep(1.5)
        asyncio.ensure_future(self.update())


if __name__ == "__main__":
    BtopServer(5678).start()
