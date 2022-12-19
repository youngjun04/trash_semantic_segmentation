# 모듈 import
import platform
from mmcv import Config
from mmseg.datasets import build_dataset
from mmseg.models import build_segmentor
from mmseg.apis import train_segmentor
from mmseg.datasets import (build_dataloader, build_dataset)
from mmseg.utils import get_device
from multiprocessing import freeze_support

import wandb
import wandb_config

from mmcv.runner.hooks import HOOKS, Hook


selfos = platform.system() 

model_dir = 'convnext'
model_name = 'upernet_convnext_tiny_fp16_512x512_160k_ade20k'
work_dir = f'./work_dirs/{model_name}'


def train():

    # config file 들고오기
    cfg = Config.fromfile(f'./configs/_TrashSEG_/{model_dir}/{model_name}.py')

    cfg.data.workers_per_gpu = 8 #num_workers
    cfg.data.samples_per_gpu = 4

    cfg.seed = 24
    cfg.gpu_ids = [0]
    cfg.work_dir = work_dir

    cfg.evaluation = dict(
        interval=1, 
        start=1,
        save_best='auto' 
    )
    
    
    cfg.optimizer_config.grad_clip = None #dict(max_norm=35, norm_type=2)

    cfg.checkpoint_config = dict(max_keep_ckpts=3, interval=1)
    cfg.log_config = dict(
        interval=50,
        hooks=[
            dict(type='TextLoggerHook'),
            #dict(type='ImageDetection'),
            #dict(type='TensorboardLoggerHook')
            #dict(type='CustomSweepHook')
            #dict(type='MMSegWandbHook', by_epoch=False) # The Wandb logger is also supported, It requires `wandb` to be installed.
            #     init_kwargs={'entity': "revanZX", # The entity used to log on Wandb
            #                  'project': "MMSeg", # Project name in WandB
            #                  'config': cfg_dict}), # Check https://docs.wandb.ai/ref/python/init for more init arguments.
    ])
    
    cfg.device = get_device()
    cfg.runner = dict(type='EpochBasedRunner', max_epochs=20)
    #cfg.load_from = './work_dirs/dyhead/best_bbox_mAP_50_epoch_12.pth'
    # build_dataset
    datasets = [build_dataset(cfg.data.train)]
    
    #print(datasets[0])

    # 모델 build 및 pretrained network 불러오기
    model = build_segmentor(cfg.model)
    model.init_weights()

    meta = dict()
    #meta['fp16'] = dict(loss_scale=dict(init_scale=512))

    # 모델 학습
    train_segmentor(model, datasets, cfg, distributed=False, validate=True, meta=meta)

if __name__ == '__main__':
    if selfos == 'Windows':
        freeze_support()
    
    train()