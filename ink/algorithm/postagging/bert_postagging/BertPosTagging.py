import os
import torch
import torch.utils.data as Data
from ....nn.models import BertLinear
from ....data import load
from ...BasicAlgorithm import BasicAlgorithm
from .dataset import Dataset
from .class_list import classlist
from .apply_text_norm import process_sent
from .evaluate_funcs import format_output


class BertPosTagging(BasicAlgorithm):
    def __init__(self, device=None):
        pos_path = load('pos')
        self.model = BertLinear(classlist)
        checkpoint = torch.load(os.path.join(pos_path, "params.ckpt"), map_location=lambda storage, loc: storage)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        super().__init__(device)

    def to(self, device):
        self.model = self.model.to(device)
        return super().to(device)

    def __call__(self, sents: list) -> list:
        """
        Args:
            sents: list[str]
                表示需要进行词性标注的字符串列表，例如，['今天天气真好']

        Return:
            list[list[tuple]]
                对于每一个输入，输出分词后每个词对应的词性标注[(词语, 词性),]
                例如，[[('今天', 'NT'), ('天气', 'NN'), ('真', 'AD'), ('好', 'VA')]]
        """
        processed_sents = [process_sent(' '.join(sent)).split(' ') for sent in sents]
        examples = [[sent, [0 for i in range(len(sent))]] for sent in processed_sents]
        dataset = Dataset(examples=examples)
        formatted_output = self.infer_epoch(Data.DataLoader(dataset, batch_size=4, num_workers=0))
        results = self.process_output(sents, formatted_output)
        return results

    def infer_epoch(self, infer_loader):
        pred, mask = [], []
        for batch in infer_loader:
            p, m = self.infer_step(batch)
            pred += p
            mask += m
        return format_output(pred, mask, classlist, dims=2)

    def infer_step(self, batch):
        x, at, y = batch
        x, at, y = x.to(self.device), at.to(self.device), y.to(self.device)
        with torch.no_grad():
            p = self.model(x, at)
            return p.cpu().tolist(), (y != -1).long().cpu().tolist()

    def process_output(self, sents, formatted_output):
        results = []
        for sent, [_, pos_tagging] in zip(sents, formatted_output):
            result = []
            for ((begin, end), tag) in pos_tagging:
                result.append((sent[begin:end], tag))
            results.append(result)
        return results
