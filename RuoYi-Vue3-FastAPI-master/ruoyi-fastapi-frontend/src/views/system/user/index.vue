<template>
  <div class="app-container">
    <el-row :gutter="20">
      <splitpanes
        :horizontal="appStore.device === 'mobile'"
        class="default-theme"
      >
        <!--部门数据-->
        <pane size="16">
          <el-col>
            <div class="head-container">
              <el-input
                v-model="deptName"
                placeholder="请输入部门名称"
                clearable
                prefix-icon="Search"
                style="margin-bottom: 20px"
              />
            </div>
            <div class="head-container">
              <el-tree
                :data="deptOptions"
                :props="{ label: 'label', children: 'children' }"
                :expand-on-click-node="false"
                :filter-node-method="filterNode"
                ref="deptTreeRef"
                node-key="id"
                highlight-current
                default-expand-all
                @node-click="handleNodeClick"
              />
            </div>
          </el-col>
        </pane>
        <!--用户数据-->
        <pane size="84">
          <el-col>
            <el-form
              :model="queryParams"
              ref="queryRef"
              :inline="true"
              v-show="showSearch"
              label-width="68px"
            >
              <el-form-item label="工号" prop="jobNumber">
                <el-input
                  v-model="queryParams.jobNumber"
                  placeholder="请输入工号"
                  clearable
                  style="width: 240px"
                  @keyup.enter="handleQuery"
                />
              </el-form-item>
              <el-form-item label="员工姓名" prop="employeeName">
                <el-input
                  v-model="queryParams.employeeName"
                  placeholder="请输入员工姓名"
                  clearable
                  style="width: 240px"
                  @keyup.enter="handleQuery"
                />
              </el-form-item>
              <el-form-item label="级别" prop="rankId">
                <el-select
                  v-model="queryParams.rankId"
                  placeholder="请选择级别"
                  clearable
                  style="width: 240px"
                >
                  <el-option
                    v-for="post in postOptions"
                    :key="post.postId"
                    :label="post.postName"
                    :value="post.postId"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="手机号码" prop="phonenumber">
                <el-input
                  v-model="queryParams.phonenumber"
                  placeholder="请输入手机号码"
                  clearable
                  style="width: 240px"
                  @keyup.enter="handleQuery"
                />
              </el-form-item>
              <el-form-item label="角色" prop="roleId">
                <el-select
                  v-model="queryParams.roleId"
                  placeholder="请选择角色"
                  clearable
                  style="width: 240px"
                >
                  <el-option
                    v-for="role in roleOptions"
                    :key="role.roleId"
                    :label="role.roleName"
                    :value="role.roleId"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="状态" prop="status">
                <el-select
                  v-model="queryParams.status"
                  placeholder="用户状态"
                  clearable
                  style="width: 240px"
                >
                  <el-option
                    v-for="dict in sys_normal_disable"
                    :key="dict.value"
                    :label="dict.label"
                    :value="dict.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" icon="Search" @click="handleQuery"
                  >搜索</el-button
                >
                <el-button icon="Refresh" @click="resetQuery">重置</el-button>
              </el-form-item>
            </el-form>

            <el-row :gutter="10" class="mb8">
              <el-col :span="1.5">
                <el-button
                  type="warning"
                  plain
                  icon="Download"
                  @click="handleExport"
                  v-hasPermi="['system:user:export']"
                  >导出</el-button
                >
              </el-col>
              <right-toolbar
                v-model:showSearch="showSearch"
                @queryTable="getList"
                :columns="columns"
              ></right-toolbar>
            </el-row>

            <el-table
              v-loading="loading"
              :data="userList"
            >
              <el-table-column
                label="工号"
                align="center"
                key="jobNumber"
                prop="jobNumber"
                v-if="columns.jobNumber.visible"
                :show-overflow-tooltip="true"
              />
              <el-table-column
                label="员工姓名"
                align="center"
                key="employeeName"
                prop="employeeName"
                v-if="columns.employeeName.visible"
                :show-overflow-tooltip="true"
              />
              <el-table-column
                label="级别"
                align="center"
                key="rankName"
                prop="rankName"
                v-if="columns.rankName.visible"
                :show-overflow-tooltip="true"
              />
              <el-table-column
                label="编制"
                align="center"
                key="deptName"
                prop="dept.deptNameWithId"
                v-if="columns.deptName.visible"
                :show-overflow-tooltip="true"
              />
              <el-table-column
                label="手机号码"
                align="center"
                key="phonenumber"
                prop="phonenumber"
                v-if="columns.phonenumber.visible"
                width="120"
              />
              <el-table-column
                label="角色"
                align="center"
                key="roleName"
                v-if="columns.roleName.visible"
                :show-overflow-tooltip="true"
              >
                <template #default="scope">
                  <el-link
                    v-if="canEditUser"
                    type="primary"
                    :underline="false"
                    @click="handleAuthRole(scope.row)"
                  >
                    {{ getRoleDisplayText(scope.row) }}
                  </el-link>
                  <span v-else style="color: var(--el-text-color-regular)">
                    {{ getRoleDisplayText(scope.row) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column
                label="状态"
                align="center"
                key="status"
                v-if="columns.status.visible"
              >
                <template #default="scope">
                  <template v-if="canEditUser">
                    <el-switch
                      v-model="scope.row.status"
                      active-value="0"
                      inactive-value="1"
                      :disabled="scope.row.userId === userStore.id"
                      @change="handleStatusChange(scope.row)"
                    ></el-switch>
                  </template>
                  <template v-else>
                    <span style="color: var(--el-text-color-regular)">
                      {{ scope.row.status === "0" ? "启用" : "停用" }}
                    </span>
                  </template>
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                align="center"
                width="200"
                class-name="small-padding fixed-width"
              >
                <template #default="scope">
                  <el-tooltip
                    content="查看"
                    placement="top"
                    v-if="scope.row.userId !== 1"
                  >
                    <el-button
                      link
                      type="primary"
                      icon="View"
                      @click="handleView(scope.row)"
                      v-hasPermi="['system:user:query']"
                    ></el-button>
                  </el-tooltip>
                  <el-tooltip
                    content="重置密码"
                    placement="top"
                    v-if="scope.row.userId !== 1 && canEditUser"
                  >
                    <el-button
                      link
                      type="primary"
                      icon="Key"
                      @click="handleResetPwd(scope.row)"
                    ></el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <pagination
              v-show="total > 0"
              :total="total"
              v-model:page="queryParams.pageNum"
              v-model:limit="queryParams.pageSize"
              @pagination="getList"
            />
          </el-col>
        </pane>
      </splitpanes>
    </el-row>

    <!-- 用户信息查看对话框 -->
    <el-dialog title="用户信息" v-model="viewOpen" width="600px" append-to-body>
      <el-form :model="viewForm" label-width="80px">
        <!-- 空对话框，具体内容后续根据数据表字段梳理后再开发 -->
        <el-empty description="用户详细信息展示区域（待开发）" />
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="viewOpen = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="User">
import useAppStore from "@/store/modules/app";
import useUserStore from "@/store/modules/user";
import {
  changeUserStatus,
  listUser,
  resetUserPwd,
  getUser,
  deptTreeSelect,
} from "@/api/system/user";
import { listPost } from "@/api/system/post";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";

const router = useRouter();
const appStore = useAppStore();
const userStore = useUserStore();
const { proxy } = getCurrentInstance();
const { sys_normal_disable } = proxy.useDict("sys_normal_disable");
// 编辑权限：管理员（角色含 admin）始终可编辑；否则依赖 system:user:edit
const canEditUser = computed(() => {
  const roles = userStore.roles || [];
  if (roles.includes("admin")) return true;
  if (!proxy?.$hasPermi) return false;
  return proxy.$hasPermi(["system:user:edit"]);
});

const userList = ref([]);
const viewOpen = ref(false);
const viewForm = ref({});
const loading = ref(true);
const showSearch = ref(true);
const total = ref(0);
const deptName = ref("");
const deptOptions = ref(undefined);
const postOptions = ref([]);
const roleOptions = ref([]);
// 记录上次查询条件（用于判断是否需要刷新角色选项）
const lastQueryKey = ref('');

// 列显隐信息

const columns = ref({
  jobNumber: { label: "工号", visible: true },
  employeeName: { label: "员工姓名", visible: true },
  rankName: { label: "级别", visible: true },
  deptName: { label: "编制", visible: true },
  phonenumber: { label: "手机号码", visible: true },
  roleName: { label: "角色", visible: true },
  status: { label: "状态", visible: true },
});

const data = reactive({
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    jobNumber: undefined,
    employeeName: undefined,
    rankId: undefined,
    phonenumber: undefined,
    roleId: undefined,
    status: undefined,
    deptId: undefined,
  },
});

const { queryParams } = toRefs(data);

/** 通过条件过滤节点  */
const filterNode = (value, data) => {
  if (!value) return true;
  return data.label.indexOf(value) !== -1;
};
/** 根据名称筛选部门树 */
watch(deptName, (val) => {
  proxy.$refs["deptTreeRef"].filter(val);
});

/**
 * 从用户列表中提取并聚合角色选项
 * @param {Array} users - 用户列表
 * @returns {Array} 角色选项数组
 */
function extractRolesFromUsers(users) {
  const roleMap = new Map();
  (users || []).forEach((item) => {
    if (item.roles && Array.isArray(item.roles)) {
      item.roles.forEach((r) => {
        const id = r.roleId || r.role_id;
        const name = r.roleName || r.role_name;
        if (id && name && !roleMap.has(id)) {
          roleMap.set(id, { roleId: id, roleName: name });
        }
      });
    }
  });
  return Array.from(roleMap.values());
}

/** 查询用户列表 */
function getList() {
  loading.value = true;
  listUser(queryParams.value).then((res) => {
    loading.value = false;
    userList.value = res.rows;
    total.value = res.total;
    // 如果角色选项为空，从当前页数据中提取（用于首次加载）
    if (roleOptions.value.length === 0) {
      roleOptions.value = extractRolesFromUsers(res.rows);
    }
  }).catch(() => {
    loading.value = false;
  });
}
/** 查询部门下拉树结构 */
function getDeptTree() {
  deptTreeSelect().then((response) => {
    deptOptions.value = response.data;
  });
}
/** 查询岗位列表 */
function getPostList() {
  listPost({ pageNum: 1, pageSize: 1000 })
    .then((response) => {
      postOptions.value = response.rows || [];
    })
    .catch(() => {
      // 如果权限不足或其他错误，静默失败，不显示岗位下拉框
      postOptions.value = [];
    });
}
/**
 * 生成查询条件的唯一标识（排除分页参数）
 * @returns {string} 查询条件标识
 */
function getQueryKey() {
  const { pageNum, pageSize, ...filterParams } = queryParams.value;
  return JSON.stringify(filterParams);
}

/**
 * 基于当前查询条件的全量用户数据聚合角色列表（避免仅限当前分页）
 * 用于角色下拉框，确保显示所有符合条件的角色选项
 * 只在查询条件变化时刷新，避免不必要的请求
 */
function refreshRoleOptions() {
  const currentQueryKey = getQueryKey();
  // 如果查询条件没有变化且已有角色选项，跳过刷新
  if (currentQueryKey === lastQueryKey.value && roleOptions.value.length > 0) {
    return;
  }
  
  // 更新查询条件标识
  lastQueryKey.value = currentQueryKey;
  
  // 构建查询参数（排除分页参数，使用全量查询）
  const { pageNum, pageSize, ...filterParams } = queryParams.value;
  const params = {
    ...filterParams,
    pageNum: 1,
    pageSize: 9999,
  };
  
  listUser(params).then((res) => {
    roleOptions.value = extractRolesFromUsers(res.rows);
  }).catch(() => {
    // 静默失败，不影响页面使用
    roleOptions.value = [];
  });
}
/** 获取角色显示文本 */
function getRoleDisplayText(row) {
  // 优先使用 roleNames（后端返回的角色名称字符串）
  if (row.roleNames) {
    return row.roleNames;
  }
  // 如果没有 roleNames，尝试从 roles 数组中提取
  if (row.roles && Array.isArray(row.roles) && row.roles.length > 0) {
    return row.roles.map(r => r.roleName || r.role_name).filter(Boolean).join(', ');
  }
  // 如果都没有，显示"未配置"
  return "未配置";
}
/** 节点单击事件 */
function handleNodeClick(data) {
  queryParams.value.deptId = data.id;
  handleQuery();
}
/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
  // 查询条件变化，需要刷新角色选项
  refreshRoleOptions();
}
/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  queryParams.value.deptId = undefined;
  proxy.$refs.deptTreeRef.setCurrentKey(null);
  handleQuery();
}
/** 查看按钮操作 */
function handleView(row) {
  const userId = row.userId;
  getUser(userId).then((response) => {
    viewForm.value = response.data;
    viewOpen.value = true;
  });
}
/**
 * 过滤查询参数，移除 undefined 和 null 值
 * @param {Object} params - 原始参数对象
 * @returns {Object} 过滤后的参数对象
 */
function filterQueryParams(params) {
  const filtered = {};
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      filtered[key] = params[key];
    }
  });
  return filtered;
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download(
    "system/user/export",
    filterQueryParams(queryParams.value),
    `user_${new Date().getTime()}.xlsx`
  );
}
/**
 * 获取用户显示名称（用于提示信息）
 * @param {Object} row - 用户行数据
 * @returns {string} 用户显示名称
 */
function getUserDisplayName(row) {
  return row.jobNumber || row.employeeName || "该用户";
}

/** 用户状态修改  */
function handleStatusChange(row) {
  const text = row.status === "0" ? "启用" : "停用";
  proxy.$modal
    .confirm(`确认要"${text}""${getUserDisplayName(row)}"用户吗?`)
    .then(() => {
      return changeUserStatus(row.userId, row.status);
    })
    .then(() => {
      proxy.$modal.msgSuccess(text + "成功");
    })
    .catch(() => {
      row.status = row.status === "0" ? "1" : "0";
    });
}

/** 跳转角色分配 */
function handleAuthRole(row) {
  router.push(`/system/user-auth/role/${row.userId}`);
}

/** 重置密码按钮操作 */
function handleResetPwd(row) {
  proxy
    .$prompt(`请输入"${getUserDisplayName(row)}"的新密码`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      closeOnClickModal: false,
      inputPattern: /^.{5,20}$/,
      inputErrorMessage: "用户密码长度必须介于 5 和 20 之间",
      inputValidator: (value) => {
        if (/<|>|"|'|\||\\/.test(value)) {
          return "不能包含非法字符：< > \" ' \\\ |";
        }
      },
    })
    .then(({ value }) => {
      resetUserPwd(row.userId, value).then(() => {
        proxy.$modal.msgSuccess("修改成功，新密码是：" + value);
      });
    })
    .catch(() => {});
}
onMounted(() => {
  getDeptTree();
  getPostList();
  // 首次加载：只获取用户列表，角色选项在查询条件变化时再加载
  getList();
});

// 返回页面时刷新列表，确保角色配置变更后能同步显示
onActivated(() => {
  // 只刷新用户列表，角色选项在查询条件未变化时不需要刷新
  getList();
});
</script>
