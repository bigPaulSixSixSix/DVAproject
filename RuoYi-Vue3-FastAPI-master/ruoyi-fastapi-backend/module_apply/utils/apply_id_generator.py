"""
申请单ID生成器（雪花算法）
"""
import time
import threading
from utils.log_util import logger


class ApplyIdGenerator:
    """申请单ID生成器（雪花算法）"""
    
    # 雪花算法参数
    WORKER_ID_BITS = 5
    DATACENTER_ID_BITS = 5
    SEQUENCE_BITS = 12
    
    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
    MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1
    SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1
    
    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS
    
    # 起始时间戳（2024-01-01 00:00:00）
    EPOCH = 1704067200000
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, worker_id: int = 1, datacenter_id: int = 1):
        """
        初始化生成器
        
        :param worker_id: 工作机器ID（0-31）
        :param datacenter_id: 数据中心ID（0-31）
        """
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f'worker_id must be between 0 and {self.MAX_WORKER_ID}')
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f'datacenter_id must be between 0 and {self.MAX_DATACENTER_ID}')
        
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
    
    def generate(self) -> str:
        """
        生成申请单ID（返回字符串格式）
        
        :return: 申请单ID（字符串）
        """
        with self._lock:
            timestamp = self._current_timestamp()
            
            # 时钟回拨检测
            if timestamp < self.last_timestamp:
                logger.error(f'时钟回拨检测到，拒绝生成ID。last_timestamp: {self.last_timestamp}, current_timestamp: {timestamp}')
                raise RuntimeError(f'时钟回拨，拒绝生成ID。时间差: {self.last_timestamp - timestamp}ms')
            
            # 同一毫秒内，序列号递增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                # 序列号溢出，等待下一毫秒
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # 新的毫秒，序列号重置为0
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # 生成ID
            id_value = (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_LEFT_SHIFT) |
                (self.datacenter_id << self.DATACENTER_ID_SHIFT) |
                (self.worker_id << self.WORKER_ID_SHIFT) |
                self.sequence
            )
            
            return str(id_value)
    
    def _current_timestamp(self) -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        """等待下一毫秒"""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp
    
    @classmethod
    def get_instance(cls) -> 'ApplyIdGenerator':
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
